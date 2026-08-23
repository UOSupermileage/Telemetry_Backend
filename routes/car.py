from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.car import DBCar
from database.team import DBTeam
from db import get_db
from schemas.car import CarCreate, Car, CarUpdate

router = APIRouter()


@router.get('/cars', response_model=list[Car])
def get_all_cars(db: Session = Depends(get_db)):
  cars = db.query(DBCar).all()
  return cars


@router.get('/cars/{car_id}', response_model=Car)
def get_car(car_id: int, db: Session = Depends(get_db)):
  car = db.get(DBCar, car_id)

  if car is None:
    raise HTTPException(status_code=404, detail='Car not found')

  return car


@router.post('/cars', response_model=Car)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
  team = db.get(DBTeam, car.team_id)

  if team is None:
    raise HTTPException(status_code=404, detail='Team not found')

  db_car = DBCar(name=car.name, year_created=car.year_created, team_id=car.team_id)

  db.add(db_car)
  db.commit()
  db.refresh(db_car)

  return db_car


@router.patch('/cars/{car_id}', response_model=Car)
def update_car(car_id: int, car_update: CarUpdate, db: Session = Depends(get_db)):
  car = db.get(DBCar, car_id)

  if car is None:
    raise HTTPException(status_code=404, detail='Car not found')

  update_data = car_update.model_dump(exclude_unset=True)

  if 'team_id' in update_data:
    team = db.get(DBTeam, update_data['team_id'])

    if team is None:
      raise HTTPException(status_code=404, detail='Team not found')

  for field, value in update_data.items():
    setattr(car, field, value)

  db.commit()
  db.refresh(car)

  return car


@router.delete('/cars/{car_id}')
def delete_car(car_id: int, db: Session = Depends(get_db)):
  car = db.get(DBCar, car_id)

  if car is None:
    raise HTTPException(status_code=404, detail='Car not found')

  db.delete(car)
  db.commit()

  return {'message': f'Delete car {car_id}'}