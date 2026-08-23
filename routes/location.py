from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.location import DBLocation
from db import get_db
from schemas.location import LocationCreate, Location, LocationUpdate

router = APIRouter()


@router.get('/locations', response_model=list[Location])
def get_all_locations(db: Session = Depends(get_db)):
  locations = db.query(DBLocation).all()
  return locations

@router.get('/locations/{location_id}', response_model=Location)
def get_location(location_id: int, db: Session = Depends(get_db)):
  location = db.get(DBLocation, location_id)

  if location is None:
    raise HTTPException(status_code=404, detail='Location not found')

  return location

@router.post('/locations', response_model=Location)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
  db_location = DBLocation(name=location.name, address=location.address)

  db.add(db_location)
  db.commit()
  db.refresh(db_location)

  return db_location

@router.patch('/locations/{location_id}', response_model=Location)
def update_location(location_id: int, location_update: LocationUpdate, db: Session = Depends(get_db)):
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
  location = db.get(DBLocation, location_id)

  if location is None:
    raise HTTPException(status_code=404, detail='Location not found')

  db.delete(location)
  db.commit()

  return {'message': f'Delete location {location_id}'}