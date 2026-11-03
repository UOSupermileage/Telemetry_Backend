import pandas as pd


def calculate_run_analytics(df: pd.DataFrame) -> dict:
  """
  Calculate summary analytics from vehicle telemetry data.
  :param df: DataFrame containing telemetry data with columns for
               speed, throttle, current, and voltage.
  :return: Dictionary containing telemetry point count and summary
             statistics for speed, throttle, current, and voltage.
  """
  # Statistics deliberately retain raw sensor units, just like SQL aggregates.
  def statistic(column, operation):
    value = getattr(df[column], operation)()
    return None if pd.isna(value) else float(value)

  return {
    'telemetry_points': len(df),
    'average_speed': statistic('speed', 'mean'),
    'max_speed': statistic('speed', 'max'),
    'average_throttle': statistic('throttle', 'mean'),
    'max_throttle': statistic('throttle', 'max'),
    'average_current': statistic('current', 'mean'),
    'max_current': statistic('current', 'max'),
    'average_voltage': statistic('voltage', 'mean'),
    'min_voltage': statistic('voltage', 'min'),
    'max_voltage': statistic('voltage', 'max')
  }
