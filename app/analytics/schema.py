from pydantic import BaseModel, Field


class RunAnalytics(BaseModel):
  run_id: int
  run_name: str = Field(..., serialization_alias='runName')
  telemetry_points: int
  duration_seconds: float | None = None
  average_speed: float | None = None
  max_speed: float | None = None
  average_throttle: float | None = None
  max_throttle: float | None = None
  average_current: float | None = None
  max_current: float | None = None
  average_voltage: float | None = None
  min_voltage: float | None = None
  max_voltage: float | None = None
