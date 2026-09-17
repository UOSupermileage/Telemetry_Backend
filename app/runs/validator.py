from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.cars.repository import DBCar
from app.driver.repository import DBDriver
from app.locations.repository import DBLocation
from app.telemetry.schema import TelemetryImportRun


def validate_run_data(db: Session, run_data: TelemetryImportRun) -> None:
  """
  Validate run data before creating a telemetry run.

  Checks that the run times are valid and that the referenced car,
  driver, and location exist in the database.

  :param db: Database session used to validate referenced records.
  :param run_data: Run data to validate.
  :raises HTTPException: 400 if ended_at is not after started_at.
  :raises HTTPException: 404 if the specified car, driver, or location is not found.
  """
  if run_data.ended_at is not None and run_data.ended_at <= run_data.started_at:
    raise HTTPException(status_code=400, detail='ended_at must be after started_at')

  if db.get(DBCar, run_data.car_id) is None:
    raise HTTPException(status_code=404, detail='Car not found')

  if db.get(DBDriver, run_data.driver_id) is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  if db.get(DBLocation, run_data.location_id) is None:
    raise HTTPException(status_code=404, detail='Location not found')