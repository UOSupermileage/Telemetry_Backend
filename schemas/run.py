from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class RunBase(BaseModel):
  car_id: int = Field(..., description='Car used for the run')
  location_id: int = Field(..., description='Location of the run')
  driver_id: int = Field(..., description='Driver of the run')
  started_at: datetime = Field(..., description='Time the run started')
  ended_at: datetime | None = Field(None, description='Time the run ended')
  notes: str | None = Field(None, description='Notes about the run')

class RunCreate(RunBase):
  pass

class Run(RunBase):
  run_id: int = Field(..., description='Unique id of the run')
  date_created: datetime = Field(..., description='Date the run was created')
  model_config = ConfigDict(from_attributes=True)

class RunUpdate(BaseModel):
  car_id: int | None = Field(None)
  location_id: int | None = Field(None)
  driver_id: int | None = Field(None)
  started_at: datetime | None = Field(None)
  ended_at: datetime | None = Field(None)
  notes: str | None = Field(None)