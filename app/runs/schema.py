from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from app.core.patch_schema import PatchSchema


class RunBase(BaseModel):
  name: str = Field(..., min_length=1, max_length=100, description='Name of the run')
  car_id: int = Field(..., description='Car used for the run')
  location_id: int = Field(..., description='Location of the run')
  driver_id: int = Field(..., description='Driver of the run')
  started_at: datetime = Field(..., description='Time the run started')
  ended_at: datetime | None = Field(None, description='Time the run ended')
  notes: str | None = Field(None, description='Notes about the run')

class RunCreate(RunBase):
  pass

class Run(BaseModel):
  name: str
  run_id: int = Field(..., description='Unique id of the run')
  car_name: str = Field(..., serialization_alias='carName')
  driver_name: str = Field(..., serialization_alias='driverName')
  location_name: str = Field(..., serialization_alias='locationName')
  started_at: datetime
  ended_at: datetime | None
  notes: str | None
  date_created: datetime = Field(..., description='Date the run was created')
  model_config = ConfigDict(from_attributes=True)

class RunUpdate(PatchSchema):
  nullable_fields = frozenset({'ended_at', 'notes'})
  name: str | None = Field(None, min_length=1, max_length=100)
  car_id: int | None = Field(None)
  location_id: int | None = Field(None)
  driver_id: int | None = Field(None)
  started_at: datetime | None = Field(None)
  ended_at: datetime | None = Field(None)
  notes: str | None = Field(None)
