from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.driver.repository import DBDriver
from app.db.connection import get_db
from app.driver.schema import DriverCreate, Driver, DriverUpdate

router = APIRouter()

@router.get('/drivers', response_model=list[Driver])
def get_all_drivers(db: Session = Depends(get_db)):
  """
  Retrieve all drivers from the database.
  :param db: Database session used to retrieve the driver data.
  :return: List of all drivers.
  """
  drivers = db.query(DBDriver).all()
  return drivers

@router.get('/drivers/{driver_id}', response_model=Driver)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
  """
  Retrieve a specific driver from the database by ID.
  :param driver_id: The unique ID of the driver.
  :param db: Database session used to retrieve the driver data.
  :return: The requested driver.
  :raises HTTPException: 404 if the driver is not found.
  """
  driver = db.get(DBDriver, driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  return driver

@router.post('/drivers', response_model=Driver)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
  """
  Create a new driver in the database.
  :param driver: Data for the driver to be created.
  :param db: Database session used to create and store the driver.
  :return: The newly created driver.
  """
  db_driver = DBDriver(first_name=driver.first_name, last_name=driver.last_name)

  db.add(db_driver)
  db.commit()
  db.refresh(db_driver)

  return db_driver

@router.patch('/drivers/{driver_id}', response_model=Driver)
def update_driver(driver_id: int, driver_update: DriverUpdate, db: Session = Depends(get_db)):
  """
  Update an existing driver in the database.
  :param driver_id: The unique ID of the driver to update.
  :param driver_update: The fields to update on the driver.
  :param db: Database session used to retrieve and update the driver.
  :return: The updated driver.
  :raises HTTPException: 404 if the driver is not found.
  """
  driver = db.get(DBDriver, driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  update_data = driver_update.model_dump(exclude_unset=True)

  for field, value in update_data.items():
    setattr(driver, field, value)

  db.commit()
  db.refresh(driver)

  return driver

@router.delete('/drivers/{driver_id}')
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
  """
  Delete a driver from the database.
  :param driver_id: The unique ID of the driver to delete.
  :param db: Database session used to retrieve and delete the driver.
  :return: Confirmation message containing the deleted driver ID.
  :raises HTTPException: 404 if the driver is not found.
  """
  driver = db.get(DBDriver, driver_id)

  if driver is None:
    raise HTTPException(status_code=404, detail='Driver not found')

  db.delete(driver)
  db.commit()

  return {'message': f'Delete driver {driver_id}'}