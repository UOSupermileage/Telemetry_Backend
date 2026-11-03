from pydantic import BaseModel, Field
from app.telemetry.units import THROTTLE, SPEED, CURRENT, VOLTAGE


class RunAnalytics(BaseModel):
  run_id: int
  run_name: str = Field(..., serialization_alias='runName')
  telemetry_points: int
  duration_seconds: float | None = Field(None, description='Telemetry span in seconds: (last tick - first tick) / 1000, within one boot; one point yields 0')
  average_speed: float | None = Field(None, description=SPEED)
  max_speed: float | None = Field(None, description=SPEED)
  average_throttle: float | None = Field(None, description=THROTTLE)
  max_throttle: float | None = Field(None, description=THROTTLE)
  average_current: float | None = Field(None, description=CURRENT)
  max_current: float | None = Field(None, description=CURRENT)
  average_voltage: float | None = Field(None, description=VOLTAGE)
  min_voltage: float | None = Field(None, description=VOLTAGE)
  max_voltage: float | None = Field(None, description=VOLTAGE)
