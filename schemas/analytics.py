from pydantic import BaseModel


class RunAnalytics(BaseModel):
  run_id: int
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
  distance: float | None = None