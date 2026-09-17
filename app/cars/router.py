from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.cars.repository import DBCar
from app.teams.repository import DBTeam
from app.db.connection import get_db
from app.cars.schema import CarCreate, Car, CarUpdate

router = APIRouter()


@router.get('/cars', response_model=list[Car])
def get_all_cars(db: Session = Depends(get_db)):
  """
  Gets all cars from the database table
  :param db: Database session used to retrieve the car data.
  :return: List of cars
  """
  cars = db.query(DBCar).all()
  return cars

@router.get('/cars/{car_id}', response_model=Car)
def get_car(car_id: int, db: Session = Depends(get_db)):
  """
  Gets a specific car from the database table by ID
  :param car_id: The unique ID of the car.
  :param db: Database session used to retrieve the car data.
  :return: The requested car.
  :raises HTTPException: 404 if the car cannot be found.
  """

  car = db.get(DBCar, car_id)
  if car is None:
    raise HTTPException(status_code=404, detail='Car not found')

  return car

@router.post('/cars', response_model=Car)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
  """
  Create a new car in the database.
  :param car: Data for the car to be created.
  :param db: Database session used to create and store the car.
  :return: The newly created car.
  :raises HTTPException: 404 if the specified team is not found.
  """

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
  """
  Update an existing car in the database.
  :param car_id: The unique ID of the car to update.
  :param car_update: The fields to update on the car.
  :param db: Database session used to retrieve and update the car.
  :return: The updated car.
  :raises HTTPException: 404 if the car or specified team is not found.
  """
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
  """
  Delete a car from the database.
  :param car_id: The unique ID of the car to delete.
  :param db: Database session used to retrieve and delete the car.
  :return: Confirmation message containing the deleted car ID.
  :raises HTTPException: 404 if the car is not found.
  """
  car = db.get(DBCar, car_id)

  if car is None:
    raise HTTPException(status_code=404, detail='Car not found')

  db.delete(car)
  db.commit()

  return {'message': f'Delete car {car_id}'}
