import pandas as pd

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.runs.repository import DBRun
from app.telemetry.repository import DBTelemetry
from app.db.connection import get_db
from app.analytics.schema import RunAnalytics
from app.analytics.calculations import calculate_run_analytics

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

  telemetry = db.query(DBTelemetry).filter(DBTelemetry.run_id == run_id).order_by(DBTelemetry.tick).all()

  if not telemetry:
    raise HTTPException(status_code=404, detail='No telemetry found for run')

  df = pd.DataFrame([{
    'tick': row.tick,
    'throttle': row.throttle,
    'speed': row.speed,
    'current': row.current,
    'voltage': row.voltage
  } for row in telemetry])

  analytics = calculate_run_analytics(df)

  analytics['run_id'] = run_id
  analytics['duration_seconds'] = (
    (run.ended_at - run.started_at).total_seconds()
    if run.ended_at else None
  )

  return analytics
