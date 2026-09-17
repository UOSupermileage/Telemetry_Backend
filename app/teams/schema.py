from pydantic import BaseModel, Field, ConfigDict

class TeamBase(BaseModel):
  team_name: str = Field(..., min_length=1, max_length=100, description='Name of the team')

class TeamCreate(TeamBase):
  pass

class Team(TeamBase):
  team_id: int = Field(..., description='Unique id of the team')
  model_config = ConfigDict(from_attributes=True)

class TeamUpdate(BaseModel):
  team_name: str | None = Field(None, min_length=1, max_length=100)