from pydantic import BaseModel, Field, ConfigDict


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


class TelemetryUpdate(BaseModel):
  throttle: float | None = Field(None, ge=0)
  speed: float | None = Field(None, ge=0)
  current: float | None = Field(None, ge=0)
  voltage: float | None = Field(None, ge=0)