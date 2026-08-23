from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.driver import DBDriver
from database.team import DBTeam
from db import get_db
from schemas.driver import DriverCreate, Driver, DriverUpdate
router = APIRouter()

@router.get('/drivers', response_model=list[Driver])
def get_all_drivers(db: Session = Depends(get_db)):
  drivers = db.query(DBDriver).all()
  return drivers

@router.get('/drivers/{driver_id}', response_model=Driver)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
  driver = db.get(DBDriver, driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  return driver


@router.post('/drivers', response_model=Driver)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
  team = db.get(DBTeam, driver.team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  db_driver = DBDriver(first_name=driver.first_name, last_name=driver.last_name, team_id=driver.team_id)

  db.add(db_driver)
  db.commit()
  db.refresh(db_driver)

  return db_driver


@router.patch('/drivers/{driver_id}', response_model=Driver)
def update_driver(driver_id: int, driver_update: DriverUpdate, db: Session = Depends(get_db)):
  driver = db.get(DBDriver, driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  update_data = driver_update.model_dump(exclude_unset=True)

  if 'team_id' in update_data:
    team = db.get(DBTeam, update_data['team_id'])

    if team is None:
      raise HTTPException(status_code=404, detail='Team not found')

  for field, value in update_data.items():
    setattr(driver, field, value)

  db.commit()
  db.refresh(driver)

  return driver


@router.delete('/drivers/{driver_id}')
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
  driver = db.get(DBDriver, driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  db.delete(driver)
  db.commit()

  return {'message': f'Delete driver {driver_id}'}