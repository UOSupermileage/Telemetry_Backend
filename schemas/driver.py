from pydantic import BaseModel, Field, ConfigDict


class DriverBase(BaseModel):
  first_name: str = Field(..., min_length=1, max_length=100, description='Drivers first name')
  last_name: str = Field(..., min_length=1, max_length=100, description='Drivers last name')


class DriverCreate(DriverBase):
  pass


class Driver(DriverBase):
  driver_id: int = Field(..., description='Drivers unique identification number')
  model_config = ConfigDict(from_attributes=True)


class DriverUpdate(BaseModel):
  first_name: str | None = Field(None, min_length=1, max_length=100)
  last_name: str | None = Field(None, min_length=1, max_length=100)