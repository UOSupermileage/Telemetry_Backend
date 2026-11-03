from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.core.patch_schema import PatchSchema
from app.telemetry.units import TICK, THROTTLE, SPEED, CURRENT, VOLTAGE


class TelemetryBase(BaseModel):
  run_id: int = Field(..., description='Run the telemetry belongs to')
  tick: int = Field(..., ge=0, description=TICK)
  throttle: float | None = Field(None, ge=0, le=1000, description=THROTTLE)
  speed: float | None = Field(None, ge=0, description=SPEED)
  current: float | None = Field(None, ge=0, description=CURRENT)
  voltage: float | None = Field(None, ge=0, description=VOLTAGE)


class TelemetryCreate(TelemetryBase):
  pass


class Telemetry(TelemetryBase):
  model_config = ConfigDict(from_attributes=True)


class TelemetryUpdate(PatchSchema):
  throttle: float | None = Field(None, ge=0, le=1000, description=THROTTLE)
  speed: float | None = Field(None, ge=0, description=SPEED)
  current: float | None = Field(None, ge=0, description=CURRENT)
  voltage: float | None = Field(None, ge=0, description=VOLTAGE)


class TelemetryImportRun(BaseModel):
  name: str = Field(..., min_length=1, max_length=100, description='Name of the run')
  car_id: int = Field(..., description='Car used for the run')
  driver_id: int = Field(..., description='Driver of the run')
  location_id: int = Field(..., description='Location of the run')
  started_at: datetime = Field(..., description='Wall-clock start timestamp; independent of sensor boot ticks')
  ended_at: datetime | None = Field(None, description='Wall-clock end timestamp; independent of sensor boot ticks')
  notes: str | None = Field(None, description='Notes about the run')


class TelemetryPoint(BaseModel):
  """Selected raw telemetry fields; absent fields stay absent in responses."""
  tick: int = Field(..., ge=0, description=TICK)
  throttle: float | None = Field(None, description=THROTTLE)
  speed: float | None = Field(None, description=SPEED)
  current: float | None = Field(None, description=CURRENT)
  voltage: float | None = Field(None, description=VOLTAGE)
