import pandas as pd

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.run import DBRun
from database.telemetry import DBTelemetry
from db import get_db
from schemas.analytics import RunAnalytics
from analytics.run import calculate_run_analytics

router = APIRouter()


@router.get('/analytics/runs/{run_id}', response_model=RunAnalytics)
def get_run_analytics(run_id: int, db: Session = Depends(get_db)):
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
