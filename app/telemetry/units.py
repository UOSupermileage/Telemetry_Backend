"""Raw sensor field descriptions shared by API schemas."""

TICK = 'Milliseconds since sensor boot; not a Unix timestamp or wall-clock time'
THROTTLE = 'Raw throttle in tenths of a percent (0–1000); divide by 10 for %'
SPEED = 'Raw speed in meters per hour (m/h); divide by 1000 for km/h'
CURRENT = 'Raw current in milliamps (mA); divide by 1000 for A'
VOLTAGE = 'Raw voltage in millivolts (mV); divide by 1000 for V'
