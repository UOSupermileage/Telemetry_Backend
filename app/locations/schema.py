from pydantic import BaseModel, Field, ConfigDict


class LocationBase(BaseModel):
  name: str = Field(..., min_length=1, max_length=200, description='Name of the location')
  address: str | None = Field(None, max_length=500, description='Address of the location')

class LocationCreate(LocationBase):
  pass

class Location(LocationBase):
  location_id: int = Field(..., description='Unique id of the location')
  model_config = ConfigDict(from_attributes=True)

class LocationUpdate(BaseModel):
  name: str | None = Field(None, min_length=1, max_length=200)
  address: str | None = Field(None, max_length=500)