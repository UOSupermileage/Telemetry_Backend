from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.cars.repository import DBCar
from app.driver.repository import DBDriver
from app.locations.repository import DBLocation
from app.runs.schema import RunCreate
from app.telemetry.schema import TelemetryImportRun


def validate_run_data(db: Session, run_data: TelemetryImportRun | RunCreate) -> None:
  """
  Validate run data before creating a telemetry run.

  Checks that the run times are valid and that the referenced car,
  driver, and location exist in the database.

  :param db: Database session used to validate referenced records.
  :param run_data: Run data to validate.
  :raises HTTPException: 400 if ended_at is not after started_at.
  :raises HTTPException: 404 if the specified car, driver, or location is not found.
  """
  validate_run_dates(run_data.started_at, run_data.ended_at)
  validate_run_references(db, run_data.car_id, run_data.driver_id, run_data.location_id)

def validate_run_dates(started_at, ended_at) -> None:
  if ended_at is not None and ended_at <= started_at:
    raise HTTPException(status_code=400, detail='ended_at must be after started_at')

def validate_run_references(db: Session, car_id: int, driver_id: int, location_id: int) -> None:
  if db.get(DBCar, car_id) is None:
    raise HTTPException(status_code=404, detail='Car not found')

  if db.get(DBDriver, driver_id) is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  if db.get(DBLocation, location_id) is None:
    raise HTTPException(status_code=404, detail='Location not found')
