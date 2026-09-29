from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.core.patch_schema import PatchSchema


class TelemetryBase(BaseModel):
  run_id: int = Field(..., description='Run the telemetry belongs to')
  tick: int = Field(..., ge=0, description='Telemetry tick')
  throttle: float | None = Field(None, ge=0, description='Throttle value')
  speed: float | None = Field(None, ge=0, description='Speed value')
  current: float | None = Field(None, ge=0, description='Current value')
  voltage: float | None = Field(None, ge=0, description='Voltage value')


class TelemetryCreate(TelemetryBase):
  pass


class Telemetry(TelemetryBase):
  model_config = ConfigDict(from_attributes=True)


class TelemetryUpdate(PatchSchema):
  throttle: float | None = Field(None, ge=0)
  speed: float | None = Field(None, ge=0)
  current: float | None = Field(None, ge=0)
  voltage: float | None = Field(None, ge=0)


class TelemetryImportRun(BaseModel):
  name: str = Field(..., min_length=1, max_length=100, description='Name of the run')
  car_id: int = Field(..., description='Car used for the run')
  driver_id: int = Field(..., description='Driver of the run')
  location_id: int = Field(..., description='Location of the run')
  started_at: datetime = Field(..., description='Time the run started')
  ended_at: datetime | None = Field(None, description='Time the run ended')
  notes: str | None = Field(None, description='Notes about the run')
