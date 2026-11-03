import asyncio
import csv
import io
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

# Tests never connect to or modify the configured database.
os.environ['DATABASE_URL'] = 'sqlite://'

from fastapi import HTTPException, UploadFile
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.main import app
from app.db.connection import Base
from app.telemetry.repository import DBTelemetry
from app.telemetry.router import import_telemetry, get_telemetry_data, export_telemetry
from app.telemetry.validator import read_telemetry_csv
from app.analytics.router import get_run_analytics
from app.analytics.calculations import calculate_run_analytics
from app.analytics.schema import RunAnalytics


@compiles(BigInteger, 'sqlite')
def sqlite_bigint(element, compiler, **kw):
  return 'INTEGER'


def upload(rows):
  return UploadFile(filename='raw.csv', file=io.BytesIO(
    ('tick,throttle,speed,current,voltage\n' + rows).encode()))


class RawUnitsTests(unittest.TestCase):
  def setUp(self):
    self.engine = create_engine('sqlite://', connect_args={'check_same_thread': False})
    Base.metadata.create_all(self.engine)
    self.db = Session(self.engine)

  def tearDown(self):
    self.db.close()
    self.engine.dispose()

  def import_rows(self, rows):
    with patch('app.telemetry.router.validate_run_data'):
      return import_telemetry(
        file=upload(rows), name='Raw', car_id=1, driver_id=1, location_id=1,
        started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ended_at=datetime(2026, 1, 2, tzinfo=timezone.utc), notes=None, db=self.db,
      )['run_id']

  def test_import_storage_response_analytics_and_export(self):
    run_id = self.import_rows('5000,423,9650,116,53400\n6000,423,9650,116,53400\n')
    stored = self.db.get(DBTelemetry, (run_id, 5000))
    self.assertEqual((stored.throttle, stored.speed, stored.current, stored.voltage),
                     (423, 9650, 116, 53400))
    points = get_telemetry_data(run_id, None, None,
      ['tick', 'throttle', 'speed', 'current', 'voltage'], 0, 100, self.db)
    self.assertEqual(points[0], dict(tick=5000, throttle=423, speed=9650, current=116, voltage=53400))
    self.assertEqual([points[0][f] / d for f, d in
                     [('throttle', 10), ('speed', 1000), ('current', 1000), ('voltage', 1000)]],
                     [42.3, 9.65, 0.116, 53.4])
    analytics = get_run_analytics(run_id, self.db)
    self.assertEqual(analytics['duration_seconds'], 1)
    for field, value in [('speed', 9650), ('throttle', 423), ('current', 116), ('voltage', 53400)]:
      self.assertEqual(analytics['average_' + field], value)
      self.assertEqual(analytics['max_' + field], value)
    self.assertEqual(RunAnalytics(**analytics).model_dump(by_alias=True)['runName'], 'Raw')
    response = export_telemetry(run_id, self.db)
    async def collect():
      return ''.join([chunk async for chunk in response.body_iterator])
    exported = asyncio.run(collect())
    rows = list(csv.DictReader(io.StringIO(exported)))
    self.assertEqual(float(rows[0]['speed']), 9650)
    reimported = read_telemetry_csv(upload(exported.split('\n', 1)[1]))
    self.assertEqual(reimported.iloc[0].to_dict(), points[0])
    stats = calculate_run_analytics(reimported)
    self.assertEqual(stats['average_current'], 116)

  def test_invalid_boot_sequences_and_throttle(self):
    for rows in ['1000,423,9650,116,53400\n0,423,9650,116,53400\n',
                 '0,423,9650,116,53400\n0,423,9650,116,53400\n',
                 '0,1001,9650,116,53400\n',
                 '4294967295,423,9650,116,53400\n1,423,9650,116,53400\n']:
      with self.subTest(rows=rows), self.assertRaises(HTTPException):
        read_telemetry_csv(upload(rows))

  def test_single_point_and_null_stats(self):
    run_id = self.import_rows('7000,,,,\n')
    result = get_run_analytics(run_id, self.db)
    self.assertEqual(result['duration_seconds'], 0)
    self.assertIsNone(result['average_speed'])
    frame = read_telemetry_csv(upload('7000,,,,\n'))
    self.assertIsNone(calculate_run_analytics(frame)['average_speed'])

  def test_selected_fields_and_schema(self):
    run_id = self.import_rows('5000,423,9650,116,53400\n')
    points = get_telemetry_data(run_id, 5000, 5000, ['speed'], 0, 100, self.db)
    self.assertEqual(points, [{'tick': 5000, 'speed': 9650}])
    schema = app.openapi()
    self.assertIn('meters per hour', schema['components']['schemas']['TelemetryPoint']['properties']['speed']['description'])
    self.assertIn('since sensor boot', schema['components']['schemas']['TelemetryPoint']['properties']['tick']['description'])

  def test_chart_sampling_spans_run_and_preserves_raw_values(self):
    run_id = self.import_rows(''.join(
      f'{i * i},423,{i},116,53400\n' for i in range(101)))
    for budget in [2, 3, 7, 10, 100, 101, 200]:
      with self.subTest(budget=budget):
        points = get_telemetry_data(run_id, None, None,
          ['speed', 'current'], 0, 1, self.db, max_points=budget)
        self.assertEqual(len(points), min(budget, 101))
        ticks = [point['tick'] for point in points]
        self.assertEqual(ticks, sorted(set(ticks)))
        self.assertEqual((ticks[0], ticks[-1]), (0, 10000))
        for point in points:
          self.assertEqual(set(point), {'tick', 'speed', 'current'})
          self.assertEqual(point['speed'] ** 2, point['tick'])
          self.assertEqual(point['current'], 116)
    self.assertEqual(get_run_analytics(run_id, self.db)['telemetry_points'], 101)
    self.assertEqual(self.db.query(DBTelemetry).filter_by(run_id=run_id).count(), 101)

  def test_chart_zoom_and_legacy_pagination(self):
    run_id = self.import_rows(''.join(
      f'{i * 1000},423,{i},116,53400\n' for i in range(30)))
    points = get_telemetry_data(run_id, 10000, 19000, ['speed'],
      0, 1000, self.db, max_points=4)
    self.assertEqual([point['tick'] for point in points], [10000, 13000, 16000, 19000])
    detailed = get_telemetry_data(run_id, 12000, 14000, ['speed'],
      0, 1000, self.db, max_points=4)
    self.assertEqual([point['tick'] for point in detailed], [12000, 13000, 14000])
    one = get_telemetry_data(run_id, 13000, 13000, ['speed'],
      0, 1000, self.db, max_points=4)
    self.assertEqual(one, [{'tick': 13000, 'speed': 13}])
    legacy = get_telemetry_data(run_id, None, None, ['speed'], 2, 3, self.db)
    self.assertEqual([point['tick'] for point in legacy], [2000, 3000, 4000])
    with self.assertRaises(HTTPException) as error:
      get_telemetry_data(run_id, 50000, 60000, ['speed'], 0, 1000, self.db, max_points=4)
    self.assertEqual(error.exception.status_code, 404)
    with self.assertRaises(HTTPException) as error:
      get_telemetry_data(run_id, None, None, ['speed'], 1, 1000, self.db, max_points=4)
    self.assertEqual(error.exception.status_code, 400)


if __name__ == '__main__':
  unittest.main()
