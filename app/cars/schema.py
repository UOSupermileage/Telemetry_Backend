from pydantic import BaseModel, Field, ConfigDict
from app.core.patch_schema import PatchSchema

## Fast API Classes
class CarBase(BaseModel):
  name: str = Field(..., min_length=1, max_length=100, description='Name of the car')
  year_created: int = Field(..., ge=1886, description='Year the car was created')
  team_id: int = Field(..., description='ID of the team running the car')

class CarCreate(CarBase):
  pass

class Car(BaseModel):
  car_id: int = Field(..., description='Unique id of the car')
  name: str
  year_created: int
  team_name: str = Field(..., serialization_alias='teamName')
  model_config = ConfigDict(from_attributes=True)

class CarUpdate(PatchSchema):
  name: str | None = Field(None, min_length=1, max_length=100)
  year_created: int | None = Field(None, ge=1886)
  team_id: int | None = Field(None)
