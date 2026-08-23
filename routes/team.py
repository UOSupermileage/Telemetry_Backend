from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.team import DBTeam
from db import get_db
from schemas.team import TeamCreate, Team, TeamUpdate

router = APIRouter()


@router.get('/teams', response_model=list[Team])
def get_all_teams(db: Session = Depends(get_db)):
  teams = db.query(DBTeam).all()
  return teams


@router.get('/teams/{team_id}', response_model=Team)
def get_team(team_id: int, db: Session = Depends(get_db)):
  team = db.get(DBTeam, team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  return team


@router.post('/teams', response_model=Team)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
  db_team = DBTeam(team_name=team.team_name)

  db.add(db_team)
  db.commit()
  db.refresh(db_team)

  return db_team


@router.patch('/teams/{team_id}', response_model=Team)
def update_team(team_id: int, team_update: TeamUpdate, db: Session = Depends(get_db)):
  team = db.get(DBTeam, team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  update_data = team_update.model_dump(exclude_unset=True)

  for field, value in update_data.items():
    setattr(team, field, value)

  db.commit()
  db.refresh(team)

  return team


@router.delete('/teams/{team_id}')
def delete_team(team_id: int, db: Session = Depends(get_db)):
  team = db.get(DBTeam, team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  db.delete(team)
  db.commit()

  return {'message': f'Delete team {team_id}'}