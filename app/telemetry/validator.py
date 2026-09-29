from fastapi import HTTPException, UploadFile
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = {'tick', 'throttle', 'speed', 'current', 'voltage'}
NUMERIC_COLUMNS = ['tick', 'throttle', 'speed', 'current', 'voltage']
NON_NEGATIVE_COLUMNS = ['throttle', 'speed', 'current', 'voltage']
MAX_CSV_BYTES = 100 * 1024 * 1024


def validate_csv_file(file: UploadFile) -> None:
  """
  Validate that the uploaded file is a CSV file.
  :param file: Uploaded file to validate.
  :raises HTTPException: 400 if the file is missing a filename or is not a CSV file.
  """
  if not file.filename or not file.filename.lower().endswith('.csv'):
    raise HTTPException(status_code=400, detail='File must be a CSV')
  file.file.seek(0, 2)
  file_size = file.file.tell()
  file.file.seek(0)
  if file_size > MAX_CSV_BYTES:
    raise HTTPException(status_code=413, detail='CSV file exceeds the 100 MB limit')

def read_telemetry_csv(file: UploadFile) -> pd.DataFrame:
  """
  Read and validate telemetry data from an uploaded CSV file.

  The CSV columns are normalized, required columns are checked, numeric
  values are converted, and telemetry values are validated.

  :param file: Uploaded CSV file containing telemetry data.
  :return: Validated telemetry data as a pandas DataFrame.
  :raises HTTPException: 400 if the CSV cannot be read or contains invalid data.
  """
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
  """
  Validate that the telemetry DataFrame contains all required columns.

  :param df: Telemetry data to validate.
  :raises HTTPException: 400 if one or more required columns are missing.
  """
  missing_columns = REQUIRED_COLUMNS - set(df.columns)

  if missing_columns:
    raise HTTPException(
      status_code=400,
      detail=f'Missing CSV columns: {sorted(missing_columns)}'
    )

def convert_numeric_columns(df: pd.DataFrame) -> None:
  """
  Convert telemetry columns to numeric values.
  Invalid values are converted to NaN for later validation.
  :param df: Telemetry DataFrame whose numeric columns should be converted.
  """
  for column in NUMERIC_COLUMNS:
    converted = pd.to_numeric(df[column], errors='coerce')
    invalid = df[column].notna() & converted.isna()
    if invalid.any():
      raise HTTPException(status_code=400, detail=f'{column} contains invalid numeric values')
    df[column] = converted

def validate_telemetry_values(df: pd.DataFrame) -> None:
  """
  Validate telemetry values and normalize the tick column.

  Checks that the DataFrame is not empty, tick values are valid and
  non-negative, ticks are unique, and non-negative telemetry columns
  do not contain negative values.

  :param df: Telemetry DataFrame to validate and normalize.
  :raises HTTPException: 400 if the telemetry data contains invalid values.
  """
  if df.empty:
    raise HTTPException(status_code=400, detail='CSV contains no telemetry data')

  if df['tick'].isna().any():
    raise HTTPException(status_code=400, detail='CSV contains invalid tick values')

  for column in NUMERIC_COLUMNS:
    if not np.isfinite(df[column].dropna()).all():
      raise HTTPException(status_code=400, detail=f'{column} must contain finite numeric values')

  if (df['tick'] < 0).any():
    raise HTTPException(status_code=400, detail='Telemetry tick cannot be negative')

  if (df['tick'] % 1 != 0).any():
    raise HTTPException(status_code=400, detail='Telemetry tick must be an integer')

  if df['tick'].duplicated().any():
    raise HTTPException(status_code=400, detail='CSV contains duplicate ticks')

  for column in NON_NEGATIVE_COLUMNS:
    if (df[column].dropna() < 0).any():
      raise HTTPException(
        status_code=400,
        detail=f'{column} cannot contain negative values'
      )

  df['tick'] = df['tick'].astype('int64')
