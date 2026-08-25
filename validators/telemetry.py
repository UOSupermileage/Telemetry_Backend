from fastapi import HTTPException, UploadFile
import pandas as pd


REQUIRED_COLUMNS = {'tick', 'throttle', 'speed', 'current', 'voltage'}
NUMERIC_COLUMNS = ['tick', 'throttle', 'speed', 'current', 'voltage']
NON_NEGATIVE_COLUMNS = ['throttle', 'speed', 'current', 'voltage']


def validate_csv_file(file: UploadFile) -> None:
  if not file.filename or not file.filename.lower().endswith('.csv'):
    raise HTTPException(status_code=400, detail='File must be a CSV')


def read_telemetry_csv(file: UploadFile) -> pd.DataFrame:
  try:
    df = pd.read_csv(file.file)
  except Exception:
    raise HTTPException(status_code=400, detail='Could not read CSV file')

  df.columns = df.columns.str.strip().str.lower()

  validate_columns(df)
  convert_numeric_columns(df)
  validate_telemetry_values(df)

  return df


def validate_columns(df: pd.DataFrame) -> None:
  missing_columns = REQUIRED_COLUMNS - set(df.columns)

  if missing_columns:
    raise HTTPException(status_code=400, detail=f'Missing CSV columns: {sorted(missing_columns)}')


def convert_numeric_columns(df: pd.DataFrame) -> None:
  for column in NUMERIC_COLUMNS:
    df[column] = pd.to_numeric(df[column], errors='coerce')


def validate_telemetry_values(df: pd.DataFrame) -> None:
  if df.empty:
    raise HTTPException(status_code=400, detail='CSV contains no telemetry data')

  if df['tick'].isna().any():
    raise HTTPException(status_code=400, detail='CSV contains invalid tick values')

  if (df['tick'] < 0).any():
    raise HTTPException(status_code=400, detail='Telemetry tick cannot be negative')

  if df['tick'].duplicated().any():
    raise HTTPException(status_code=400, detail='CSV contains duplicate ticks')

  for column in NON_NEGATIVE_COLUMNS:
    if (df[column].dropna() < 0).any():
      raise HTTPException(status_code=400, detail=f'{column} cannot contain negative values')

  df['tick'] = df['tick'].astype('int64')