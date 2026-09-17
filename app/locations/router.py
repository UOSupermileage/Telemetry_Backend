from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.locations.repository import DBLocation
from app.db.connection import get_db
from app.locations.schema import LocationCreate, Location, LocationUpdate

router = APIRouter()


@router.get('/locations', response_model=list[Location])
def get_all_locations(db: Session = Depends(get_db)):
  """
  Retrieve all locations from the database.
  :param db: Database session used to retrieve the location data.
  :return: List of all locations.
  """
  locations = db.query(DBLocation).all()
  return locations

@router.get('/locations/{location_id}', response_model=Location)
def get_location(location_id: int, db: Session = Depends(get_db)):
  """
  Retrieve a specific location from the database by ID.
  :param location_id: The unique ID of the location.
  :param db: Database session used to retrieve the location data.
  :return: The requested location.
  :raises HTTPException: 404 if the location is not found.
  """
  location = db.get(DBLocation, location_id)

  if location is None:
    raise HTTPException(status_code=404, detail='Location not found')

  return location

@router.post('/locations', response_model=Location)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
  """
  Create a new location in the database.
  :param location: Data for the location to be created.
  :param db: Database session used to create and store the location.
  :return: The newly created location.
  """
  db_location = DBLocation(name=location.name, address=location.address)

  db.add(db_location)
  db.commit()
  db.refresh(db_location)

  return db_location

@router.patch('/locations/{location_id}', response_model=Location)
def update_location(location_id: int, location_update: LocationUpdate, db: Session = Depends(get_db)):
  """
  Update an existing location in the database.
  :param location_id: The unique ID of the location to update.
  :param location_update: The fields to update on the location.
  :param db: Database session used to retrieve and update the location.
  :return: The updated location.
  :raises HTTPException: 404 if the location is not found.
  """
  location = db.get(DBLocation, location_id)

  if location is None:
    raise HTTPException(status_code=404, detail='Location not found')

  update_data = location_update.model_dump(exclude_unset=True)

  for field, value in update_data.items():
    setattr(location, field, value)

  db.commit()
  db.refresh(location)

  return location

@router.delete('/locations/{location_id}')
def delete_location(location_id: int, db: Session = Depends(get_db)):
  """
  Delete a location from the database.
  :param location_id: The unique ID of the location to delete.
  :param db: Database session used to retrieve and delete the location.
  :return: Confirmation message containing the deleted location ID.
  :raises HTTPException: 404 if the location is not found.
  """
  location = db.get(DBLocation, location_id)

  if location is None:
    raise HTTPException(status_code=404, detail='Location not found')

  db.delete(location)
  db.commit()

  return {'message': f'Delete location {location_id}'}