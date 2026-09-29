from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.db.connection import get_db
from app.runs.repository import DBRun
from app.runs.schema import Run, RunCreate, RunUpdate
from app.runs.validator import validate_run_data, validate_run_dates, validate_run_references

router = APIRouter()


@router.get('/runs', response_model=list[Run])
def get_all_runs(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
  return (
    db.query(DBRun)
    .options(joinedload(DBRun.car), joinedload(DBRun.driver), joinedload(DBRun.location))
    .order_by(DBRun.run_id)
    .offset(offset)
    .limit(limit)
    .all()
  )


@router.get('/runs/{run_id}', response_model=Run)
def get_run(run_id: int, db: Session = Depends(get_db)):
  run = (
    db.query(DBRun)
    .options(joinedload(DBRun.car), joinedload(DBRun.driver), joinedload(DBRun.location))
    .filter(DBRun.run_id == run_id)
    .first()
  )
  if run is None:
    raise HTTPException(status_code=404, detail='Run not found')
  return run


@router.post('/runs', response_model=Run, status_code=status.HTTP_201_CREATED)
def create_run(run_data: RunCreate, db: Session = Depends(get_db)):
  validate_run_data(db, run_data)
  run = DBRun(**run_data.model_dump())
  try:
    db.add(run)
    db.commit()
    db.refresh(run)
  except SQLAlchemyError:
    db.rollback()
    raise HTTPException(status_code=500, detail='Failed to create run')
  return run


@router.patch('/runs/{run_id}', response_model=Run)
def update_run(run_id: int, run_update: RunUpdate, db: Session = Depends(get_db)):
  run = db.query(DBRun).filter(DBRun.run_id == run_id).first()
  if run is None:
    raise HTTPException(status_code=404, detail='Run not found')

  update_data = run_update.model_dump(exclude_unset=True)
  new_car_id = update_data.get('car_id', run.car_id)
  new_driver_id = update_data.get('driver_id', run.driver_id)
  new_location_id = update_data.get('location_id', run.location_id)
  new_started_at = update_data.get('started_at', run.started_at)
  new_ended_at = update_data.get('ended_at', run.ended_at)

  validate_run_dates(new_started_at, new_ended_at)
  validate_run_references(db, new_car_id, new_driver_id, new_location_id)

  for field, value in update_data.items():
    setattr(run, field, value)

  try:
    db.commit()
    db.refresh(run)
  except SQLAlchemyError:
    db.rollback()
    raise HTTPException(status_code=500, detail='Failed to update run')
  return run


@router.delete('/runs/{run_id}')
def delete_run(run_id: int, db: Session = Depends(get_db)):
  run = db.get(DBRun, run_id)
  if run is None:
    raise HTTPException(status_code=404, detail='Run not found')

  db.delete(run)
  try:
    db.commit()
  except SQLAlchemyError:
    db.rollback()
    raise HTTPException(status_code=500, detail='Failed to delete run')

  return {'message': f'Deleted run {run_id} and its telemetry'}
