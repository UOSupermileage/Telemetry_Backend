from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.teams.repository import DBTeam
from app.db.connection import get_db
from app.teams.schema import TeamCreate, Team, TeamUpdate

router = APIRouter()


@router.get('/teams', response_model=list[Team])
def get_all_teams(db: Session = Depends(get_db)):
  """
  Retrieve all teams from the database.
  :param db: Database session used to retrieve the team data.
  :return: List of all teams.
  """
  teams = db.query(DBTeam).all()
  return teams

@router.get('/teams/{team_id}', response_model=Team)
def get_team(team_id: int, db: Session = Depends(get_db)):
  """
  Retrieve a specific team from the database by ID.
  :param team_id: The unique ID of the team.
  :param db: Database session used to retrieve the team data.
  :return: The requested team.
  :raises HTTPException: 404 if the team is not found.
  """

  team = db.get(DBTeam, team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  return team

@router.post('/teams', response_model=Team)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
  """
  Create a new team in the database.
  :param team: Data for the team to be created.
  :param db: Database session used to create and store the team.
  :return: The newly created team.
  """

  db_team = DBTeam(team_name=team.team_name)

  db.add(db_team)
  db.commit()
  db.refresh(db_team)

  return db_team

@router.patch('/teams/{team_id}', response_model=Team)
def update_team(team_id: int, team_update: TeamUpdate, db: Session = Depends(get_db)):
  """
  Update an existing team in the database.
  :param team_id: The unique ID of the team to update.
  :param team_update: The fields to update on the team.
  :param db: Database session used to retrieve and update the team.
  :return: The updated team.
  :raises HTTPException: 404 if the team is not found.
  """
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
  """
  Delete a team from the database.
  :param team_id: The unique ID of the team to delete.
  :param db: Database session used to retrieve and delete the team.
  :return: Confirmation message containing the deleted team ID.
  :raises HTTPException: 404 if the team is not found.
  """
  team = db.get(DBTeam, team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  db.delete(team)
  db.commit()

  return {'message': f'Delete team {team_id}'}