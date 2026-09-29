from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.runs.repository import DBRun
from app.telemetry.repository import DBTelemetry
from app.db.connection import get_db
from app.analytics.schema import RunAnalytics

router = APIRouter()


@router.get('/analytics/runs/{run_id}', response_model=RunAnalytics)
def get_run_analytics(run_id: int, db: Session = Depends(get_db)):
  """
  Calculate analytics for a specific run from its telemetry data.
  :param run_id: The unique ID of the run to calculate analytics for.
  :param db: Database session used to retrieve the run and telemetry data.
  :return: Run analytics including telemetry statistics and run duration.
  :raises HTTPException: 404 if the run or its telemetry cannot be found.
  """

  run = db.get(DBRun, run_id)
  if run is None:
    raise HTTPException(status_code=404, detail='Run not found')

  aggregates = db.execute(
    select(
      func.count(DBTelemetry.tick),
      func.avg(DBTelemetry.speed),
      func.max(DBTelemetry.speed),
      func.avg(DBTelemetry.throttle),
      func.max(DBTelemetry.throttle),
      func.avg(DBTelemetry.current),
      func.max(DBTelemetry.current),
      func.avg(DBTelemetry.voltage),
      func.min(DBTelemetry.voltage),
      func.max(DBTelemetry.voltage),
    ).where(DBTelemetry.run_id == run_id)
  ).one()

  if aggregates[0] == 0:
    raise HTTPException(status_code=404, detail='No telemetry found for run')
  analytics = dict(zip((
    'telemetry_points',
    'average_speed', 'max_speed',
    'average_throttle', 'max_throttle',
    'average_current', 'max_current',
    'average_voltage', 'min_voltage', 'max_voltage',
  ), aggregates))
  analytics.update(run_id=run_id, run_name=run.name, duration_seconds=(
    (run.ended_at - run.started_at).total_seconds()
    if run.ended_at else None
  ))

  return analytics
