"""Read-only PostgreSQL unit profile. Run from the project root; prints no credentials.

Ranges are evidence for review, never proof of conversion. No data is changed.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text
from app.db.connection import engine


def main():
  try:
    with engine.connect() as connection:
      with connection.begin():
        connection.execute(text('SET TRANSACTION READ ONLY'))
        connection.execute(text("SET LOCAL statement_timeout = '20s'"))
        rows = connection.execute(text('''
          SELECT run_id, count(*) AS points, min(tick) AS first_tick, max(tick) AS last_tick,
            min(throttle) AS min_throttle, max(throttle) AS max_throttle,
            min(speed) AS min_speed, max(speed) AS max_speed,
            min(current) AS min_current, max(current) AS max_current,
            min(voltage) AS min_voltage, max(voltage) AS max_voltage,
            count(*) FILTER (WHERE throttle > 1000) AS throttle_out_of_contract,
            count(*) FILTER (WHERE voltage > 0 AND voltage < 1000) AS low_voltage_review,
            count(*) FILTER (WHERE voltage >= 1000) AS raw_scale_voltage,
            count(*) FILTER (WHERE throttle <> trunc(throttle::numeric)
              OR speed <> trunc(speed::numeric) OR current <> trunc(current::numeric)
              OR voltage <> trunc(voltage::numeric)) AS fractional_rows_review
          FROM telemetry GROUP BY run_id ORDER BY run_id
        ''')).mappings().all()
        print(json.dumps([dict(row) for row in rows], indent=2, default=str))
  except Exception as error:
    # SQLAlchemy exception strings can contain connection details.
    print(f'Read-only audit unavailable: {type(error).__name__}', file=sys.stderr)
    return 1
  finally:
    engine.dispose()
  return 0


if __name__ == '__main__':
  raise SystemExit(main())
