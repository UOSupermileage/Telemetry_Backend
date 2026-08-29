import pandas as pd


def calculate_run_analytics(df: pd.DataFrame) -> dict:
  return {
    'telemetry_points': len(df),
    'average_speed': df['speed'].mean(),
    'max_speed': df['speed'].max(),
    'average_throttle': df['throttle'].mean(),
    'max_throttle': df['throttle'].max(),
    'average_current': df['current'].mean(),
    'max_current': df['current'].max(),
    'average_voltage': df['voltage'].mean(),
    'min_voltage': df['voltage'].min(),
    'max_voltage': df['voltage'].max()
  }