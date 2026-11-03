import csv
import io
from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from sqlalchemy import func, insert, or_, select
from app.runs.repository import DBRun
from app.telemetry.repository import DBTelemetry
from app.db.connection import get_db
from app.telemetry.schema import TelemetryImportRun, TelemetryPoint
from app.telemetry.units import TICK
from app.runs.validator import validate_run_data
from app.telemetry.validator import validate_csv_file, read_telemetry_csv

router = APIRouter()
CSV_COLUMNS = ('tick', 'throttle', 'speed', 'current', 'voltage')


@router.post('/telemetry/import')
def import_telemetry(
    file: UploadFile = File(...),
    name: str = Form(..., min_length=1, max_length=100),
    car_id: int = Form(...),
    driver_id: int = Form(...),
    location_id: int = Form(...),
    started_at: datetime = Form(..., description='Wall-clock start timestamp; independent of sensor boot ticks'),
    ended_at: datetime | None = Form(None, description='Wall-clock end timestamp; independent of sensor boot ticks'),
    notes: str | None = Form(None),
    db: Session = Depends(get_db)
):
  """
  Import raw telemetry and create a run. CSV units: tick ms since boot,
  throttle tenths of a percent, speed m/h, current mA, voltage mV.
  Ticks must increase within one boot; split resets/rollovers into separate runs.
  The CSV file is validated and its telemetry data is stored in the
  database along with the associated run information.

  :param file: CSV file containing the telemetry data.
  :param name: Human-readable name for the run.
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
    name=name,
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
      {'run_id': db_run.run_id, **row}
      for row in df[list(CSV_COLUMNS)].to_dict(orient='records')
    ]

    db.execute(insert(DBTelemetry), telemetry_data)
    db.commit()

  except SQLAlchemyError:
    db.rollback()
    raise HTTPException(status_code=500, detail='Failed to import telemetry')

  return {
    'message': 'Telemetry imported successfully',
    'run_id': db_run.run_id,
    'runName': db_run.name,
    'telemetry_rows': len(df)
  }


@router.get('/telemetry/export')
def export_telemetry(run_id: int, db: Session = Depends(get_db)):
  """
  Export raw sensor units: tick ms since boot, throttle tenths of a percent,
  speed m/h, current mA, voltage mV. No display conversions are applied.
  :param run_id: ID of the run whose telemetry should be exported.
  :param db: Database session used to retrieve the telemetry data.
  :return: Streaming CSV response containing the run's telemetry data.
  :raises HTTPException: 404 if no telemetry is found for the specified run.
  """
  # Query all telemetry data with run id
  exists = db.scalar(
    select(DBTelemetry.tick).where(DBTelemetry.run_id == run_id).limit(1)
  )
  if exists is None:
    raise HTTPException(status_code=404, detail=f"No telemetry found for run {run_id}")

  query = db.execute(
    select(*[getattr(DBTelemetry, column) for column in CSV_COLUMNS])
    .where(DBTelemetry.run_id == run_id)
    .order_by(DBTelemetry.tick)
    .execution_options(yield_per=1000, stream_results=True)
  )

  def csv_rows():
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)
    try:
      for row in query:
        writer.writerow(row)
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)
    finally:
      query.close()
  return StreamingResponse(
    csv_rows(),
    media_type='text/csv',
    headers={
      'Content-Disposition': (
        f'attachment; filename="telemetry_run_{run_id}.csv"'
      )
    },
  )


@router.get("/telemetry/data", response_model=list[TelemetryPoint], response_model_exclude_unset=True)
def get_telemetry_data(
    run_id: int,
    start_tick: int | None = Query(None, ge=0, description=TICK),
    end_tick: int | None = Query(None, ge=0, description=TICK),
    fields: list[
      Literal["tick", "throttle", "speed", "current", "voltage"]
    ] = Query(["tick", "speed"]),
    offset: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
    max_points: Annotated[int | None, Query(ge=2, le=10000, description=(
      'Optional chart point budget across the entire tick range. Returns original '
      'readings sampled evenly by row position, including endpoints. Overrides '
      'limit; offset must be 0. Narrow start_tick/end_tick when zooming.'
    ))] = None,
):
  """Return raw readings, optionally sampled across the requested range for charts.

  Without max_points, offset/limit retain their original pagination behavior.
  Sampling can omit short-lived extrema; use full-resolution analytics for stats.
  """
  if max_points is not None and offset != 0:
    raise HTTPException(status_code=400, detail='offset must be 0 when max_points is provided')
  if start_tick is not None and end_tick is not None:
    if start_tick > end_tick:
      raise HTTPException(
        status_code=400,
        detail="start_tick must be less than or equal to end_tick",
      )

  # Map API field names to database columns
  available_columns = {
    "tick": DBTelemetry.tick,
    "throttle": DBTelemetry.throttle,
    "speed": DBTelemetry.speed,
    "current": DBTelemetry.current,
    "voltage": DBTelemetry.voltage,
  }

  # Make sure tick is included so the returned data can still be
  # associated with a point in time.
  fields = list(dict.fromkeys(fields))
  if "tick" not in fields:
    fields.insert(0, "tick")

  selected_columns = [
    available_columns[field]
    for field in fields
  ]

  query = (
    db.query(*selected_columns)
    .filter(DBTelemetry.run_id == run_id)
  )

  if start_tick is not None:
    query = query.filter(DBTelemetry.tick >= start_tick)

  if end_tick is not None:
    query = query.filter(DBTelemetry.tick <= end_tick)

  if max_points is None:
    telemetry = query.order_by(DBTelemetry.tick).offset(offset).limit(limit).all()
  else:
    # Window functions keep the full scan in the database and transfer only the
    # bounded result. One statement gives the count and samples one snapshot.
    ranked = query.add_columns(
      func.row_number().over(order_by=DBTelemetry.tick).label('_position'),
      func.count().over().label('_total'),
    ).subquery()
    position, total = ranked.c._position, ranked.c._total
    denominator = func.nullif(total - 1, 0)
    # Select the first row and each transition between evenly spaced rank bins.
    # For N > budget this selects exactly budget rows, including both endpoints.
    current_bin = ((position - 1) * (max_points - 1)) // denominator
    previous_bin = ((position - 2) * (max_points - 1)) // denominator
    telemetry = db.execute(
      select(*(ranked.c[field] for field in fields))
      .where(or_(total <= max_points, position == 1, current_bin > previous_bin))
      .order_by(ranked.c.tick)
    ).all()

  if not telemetry:
    raise HTTPException(
      status_code=404,
      detail=f"No telemetry found for run {run_id}",
    )

  return [dict(zip(fields, row)) for row in telemetry]
