from fastapi import HTTPException
from sqlalchemy.orm import Session

from database.car import DBCar
from database.driver import DBDriver
from database.location import DBLocation
from schemas.telemetry import TelemetryImportRun


def validate_run_data(db: Session, run_data: TelemetryImportRun) -> None:
  if run_data.ended_at is not None and run_data.ended_at <= run_data.started_at:
    raise HTTPException(status_code=400, detail='ended_at must be after started_at')

  if db.get(DBCar, run_data.car_id) is None:
    raise HTTPException(status_code=404, detail='Car not found')

  if db.get(DBDriver, run_data.driver_id) is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  if db.get(DBLocation, run_data.location_id) is None:
    raise HTTPException(status_code=404, detail='Location not found')