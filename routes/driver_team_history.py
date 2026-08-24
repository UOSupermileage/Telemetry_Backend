from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.driver import DBDriver
from database.driver_team_history import DBDriverTeamHistory
from database.team import DBTeam
from db import get_db
from schemas.driver_team_history import DriverTeamHistoryCreate, DriverTeamHistory, DriverTeamHistoryUpdate

router = APIRouter()


def history_overlaps(db: Session, driver_id: int, started_at, ended_at, exclude_history_id: int | None = None):
  query = db.query(DBDriverTeamHistory).filter(DBDriverTeamHistory.driver_id == driver_id)

  if exclude_history_id is not None:
    query = query.filter(DBDriverTeamHistory.history_id != exclude_history_id)

  if ended_at is None:
    query = query.filter(
      or_(
        DBDriverTeamHistory.ended_at.is_(None),
        DBDriverTeamHistory.ended_at > started_at
      )
    )
  else:
    query = query.filter(
      DBDriverTeamHistory.started_at < ended_at,
      or_(
        DBDriverTeamHistory.ended_at.is_(None),
        DBDriverTeamHistory.ended_at > started_at
      )
    )

  return query.first() is not None


@router.get('/driver-team-history', response_model=list[DriverTeamHistory])
def get_all_driver_team_history(db: Session = Depends(get_db)):
  history = db.query(DBDriverTeamHistory).all()
  return history


@router.get('/driver-team-history/{history_id}', response_model=DriverTeamHistory)
def get_driver_team_history(history_id: int, db: Session = Depends(get_db)):
  history = db.get(DBDriverTeamHistory, history_id)

  if history is None:
    raise HTTPException(status_code=404, detail='Driver team history not found')

  return history


@router.post('/driver-team-history', response_model=DriverTeamHistory)
def create_driver_team_history(history: DriverTeamHistoryCreate, db: Session = Depends(get_db)):
  if history.ended_at is not None and history.ended_at <= history.started_at:
    raise HTTPException(status_code=400, detail='ended_at must be after started_at')

  driver = db.get(DBDriver, history.driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  team = db.get(DBTeam, history.team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  if history_overlaps(db, history.driver_id, history.started_at, history.ended_at):
    raise HTTPException(status_code=409, detail='Driver already has a team assignment during this period')

  db_history = DBDriverTeamHistory(
    driver_id=history.driver_id,
    team_id=history.team_id,
    started_at=history.started_at,
    ended_at=history.ended_at
  )

  db.add(db_history)
  db.commit()
  db.refresh(db_history)

  return db_history


@router.patch('/driver-team-history/{history_id}', response_model=DriverTeamHistory)
def update_driver_team_history(history_id: int, history_update: DriverTeamHistoryUpdate, db: Session = Depends(get_db)):
  history = db.get(DBDriverTeamHistory, history_id)

  if history is None:
    raise HTTPException(status_code=404, detail='Driver team history not found')

  update_data = history_update.model_dump(exclude_unset=True)

  new_driver_id = update_data.get('driver_id', history.driver_id)
  new_team_id = update_data.get('team_id', history.team_id)
  new_started_at = update_data.get('started_at', history.started_at)
  new_ended_at = update_data.get('ended_at', history.ended_at)

  if new_ended_at is not None and new_ended_at <= new_started_at:
    raise HTTPException(status_code=400, detail='ended_at must be after started_at')

  driver = db.get(DBDriver, new_driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  team = db.get(DBTeam, new_team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  if history_overlaps(db, new_driver_id, new_started_at, new_ended_at, history_id):
    raise HTTPException(status_code=409, detail='Driver already has a team assignment during this period')

  for field, value in update_data.items():
    setattr(history, field, value)

  db.commit()
  db.refresh(history)

  return history


@router.delete('/driver-team-history/{history_id}')
def delete_driver_team_history(history_id: int, db: Session = Depends(get_db)):
  history = db.get(DBDriverTeamHistory, history_id)

  if history is None:
    raise HTTPException(status_code=404, detail='Driver team history not found')

  db.delete(history)
  db.commit()

  return {'message': f'Delete driver team history {history_id}'}