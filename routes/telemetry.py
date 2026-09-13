import csv
import io
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from database.run import DBRun
from database.telemetry import DBTelemetry
from db import get_db
from schemas.telemetry import TelemetryImportRun
from validators.run import validate_run_data
from validators.telemetry import validate_csv_file, read_telemetry_csv
router = APIRouter()


@router.post('/telemetry/import')
def import_telemetry(
    file: UploadFile = File(...),
    car_id: int = Form(...),
    driver_id: int = Form(...),
    location_id: int = Form(...),
    started_at: datetime = Form(...),
    ended_at: datetime | None = Form(None),
    notes: str | None = Form(None),
    db: Session = Depends(get_db)
):
  """
  Import telemetry data from a CSV file and create a new run.
  The CSV file is validated and its telemetry data is stored in the
  database along with the associated run information.

  :param file: CSV file containing the telemetry data.
  :param car_id: ID of the car associated with the run.
  :param driver_id: ID of the driver associated with the run.
  :param location_id: ID of the location where the run took place.
  :param started_at: Start time of the run.
  :param ended_at: End time of the run, if the run has ended.
  :param notes: Optional notes associated with the run.
  :param db: Database session used to store the run and telemetry data.
  :return: Confirmation message containing the run ID and number of telemetry rows imported.
  :raises HTTPException: 500 if the telemetry data cannot be stored.
  """
  validate_csv_file(file)

  run_data = TelemetryImportRun(
    car_id=car_id,
    driver_id=driver_id,
    location_id=location_id,
    started_at=started_at,
    ended_at=ended_at,
    notes=notes
  )

  validate_run_data(db, run_data)

  df = read_telemetry_csv(file)

  try:
    db_run = DBRun(**run_data.model_dump())
    db.add(db_run)
    db.flush()

    telemetry_data: list[dict[str, Any]] = [
      {str(key): value for key, value in row.items()}
      for row in df[['tick', 'throttle', 'speed', 'current', 'voltage']].to_dict(orient='records')
    ]

    for row in telemetry_data:
      row['run_id'] = db_run.run_id

    db.bulk_insert_mappings(DBTelemetry, telemetry_data)
    db.commit()

  except SQLAlchemyError:
    db.rollback()
    raise HTTPException(status_code=500, detail='Failed to import telemetry')

  return {
    'message': 'Telemetry imported successfully',
    'run_id': db_run.run_id,
    'telemetry_rows': len(telemetry_data)
  }


@router.get('/telemetry/export')
def export_telemetry(run_id: int,db: Session = Depends(get_db)):
  """
  Export telemetry data for a run as a CSV file.
  :param run_id: ID of the run whose telemetry should be exported.
  :param db: Database session used to retrieve the telemetry data.
  :return: Streaming CSV response containing the run's telemetry data.
  :raises HTTPException: 404 if no telemetry is found for the specified run.
  """
  #Query all telemetry data with run id
  telemetry = (
    db.query(DBTelemetry)
    .filter(DBTelemetry.run_id == run_id)
    .all()
  )

  if not telemetry:
    raise HTTPException(
      status_code=404,
      detail=f"No telemetry found for run {run_id}",
    )

  output = io.StringIO()
  writer = csv.writer(output)

  #Build column headers
  writer.writerow([
    'tick',
    'throttle',
    'speed',
    'current',
    'voltage',
  ])

  #Write telemetry values to each column
  for row in telemetry:
    writer.writerow([
      row.tick,
      row.throttle,
      row.speed,
      row.current,
      row.voltage,
    ])

  output.seek(0)

  #Export CSV for Download
  return StreamingResponse(
    iter([output.getvalue()]),
    media_type='text/csv',
    headers={
      'Content-Disposition': (
        f'attachment; filename="telemetry_run_{run_id}.csv"'
      )
    },
  )
