from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from app.core.patch_schema import PatchSchema


class DriverTeamHistoryBase(BaseModel):
  driver_id: int = Field(..., description='Driver assigned to the team')
  team_id: int = Field(..., description='Team the driver belongs to')
  started_at: datetime = Field(..., description='When the driver joined the team')
  ended_at: datetime | None = Field(None, description='When the driver left the team')

class DriverTeamHistoryCreate(DriverTeamHistoryBase):
  pass

class DriverTeamHistory(BaseModel):
  history_id: int = Field(..., description='Unique id of the driver team history record')
  driver_name: str = Field(..., serialization_alias='driverName')
  team_name: str = Field(..., serialization_alias='teamName')
  started_at: datetime
  ended_at: datetime | None
  model_config = ConfigDict(from_attributes=True)

class DriverTeamHistoryUpdate(PatchSchema):
  nullable_fields = frozenset({'ended_at'})
  driver_id: int | None = Field(None, description='Driver assigned to the team')
  team_id: int | None = Field(None, description='Team the driver belongs to')
  started_at: datetime | None = Field(None, description='When the driver joined the team')
  ended_at: datetime | None = Field(None, description='When the driver left the team')
