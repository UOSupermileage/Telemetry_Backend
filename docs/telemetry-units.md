# Telemetry unit contract and audit

The API and CSV use raw sensor units throughout. The frontend performs display
conversion once. Endpoint paths, selected-field behavior, CSV headers, analytics
field names, and the `runName` alias are preserved.

| Field | Stored / API / CSV unit | Frontend display |
| --- | --- | --- |
| tick | integer milliseconds since sensor boot | ms since boot |
| throttle | tenths of a percent, 0–1000 | divide by 10 for % |
| speed | meters per hour (m/h) | divide by 1000 for km/h |
| current | milliamps (mA) | divide by 1000 for A |
| voltage | millivolts (mV) | divide by 1000 for V |

Reference supplied for the contract:
https://github.com/UOSupermileage/UOSM-TelemetryDataProcessing
The repository landing page was accessible during the audit, but source-file
retrieval was unavailable. The explicit sensor contract supplied with this change
is authoritative; upstream conversion code was not independently verified.

## Trace and changes

- `telemetry/validator.py` parses numeric CSV columns without rescaling. Import
  inserts those values directly into `DBTelemetry`. New imports enforce throttle
  <= 1000 and increasing acquisition-order ticks, in addition to existing checks.
- `telemetry/repository.py` and `db/schema.sql` store tick as BIGINT and sensor
  channels as floating-point numeric values. Storage types and existing database
  constraints are unchanged. No unit conversion occurs in the database layer.
- `/telemetry/data` selects stored values directly. Its new response schema
  documents units while preserving omitted unselected fields and explicit nulls.
  Tick filters are boot milliseconds, not epoch times.
- `/telemetry/export` writes selected database values directly, with unchanged
  headers. Export/import round trips must not apply frontend display conversions.
- `/analytics/runs/{run_id}` uses SQL average/min/max in the source units. The
  DataFrame statistics helper also retains raw units and now returns null for
  missing statistics. Averages remain sample-weighted, not time-weighted.
- `duration_seconds` previously used run start/end wall-clock timestamps. It now
  uses `(max(tick) - min(tick)) / 1000`, the sum of adjacent positive tick
  differences within a valid single-boot run. A single point yields zero;
  no telemetry still yields 404. Gaps count toward elapsed time. Run timestamps
  remain independent wall-clock metadata and do not anchor sensor boot time.

## Derived quantities and discontinuities

There are no existing distance, power, or energy calculations or response fields.
No new response fields are introduced. Future calculations must integrate over
valid, ordered intervals within one boot. For `dt = (tick[i+1]-tick[i])/1000`
seconds, a trapezoidal estimate would use:

- Distance in **meters**: `((speed[i] + speed[i+1])/2) * dt / 3600`.
  Divide that result by 1000 for kilometers.
- Power in **watts**: `current * voltage / 1_000_000` (mA × mV to A × V).
- Energy in **joules**: `((power[i] + power[i+1])/2) * dt`.
  Divide joules by 3600 for watt-hours, or by 3,600,000 for kWh.

Missing speed skips distance for that interval; missing current or voltage skips
energy for that interval. Do not treat missing samples as zero. Report coverage
if such derived fields are introduced. The contract and existing validation only
allow nonnegative current, so signed regenerative energy would require agreement.

The `(run_id, tick)` primary key has no acquisition sequence or boot identifier.
Sorting ticks cannot recover acquisition order across resets, and repeated ticks
cannot coexist. New CSVs with decreasing or duplicate ticks are rejected: split
boot resets and rollovers into separate runs before importing. Do not unwrap
rollover by assuming a 32-bit counter: counter width and reset markers are not
specified. Supporting multiple boots in one run requires a separate schema/API
design with boot IDs or acquisition sequence and a confirmed rollover policy.
Already imported, sorted multi-boot data cannot be reliably detected or repaired
from this schema alone; its duration may be unreliable. Do not infer epoch time
from tick magnitude or infer sensor boot time from run.started_at.

## Existing-record evidence (2026-10-31)

Ran `scripts/audit_telemetry_units.py` against the configured PostgreSQL database
inside a READ ONLY transaction. It contains only profiling SELECTs and session
settings. It reports candidate anomalies; it never rescales or writes records.

| Run | Points | Tick range (ms) | Max speed (m/h) | Current range (mA) | Voltage range (mV) |
| --- | ---: | --- | ---: | --- | --- |
| 1 | 35,585 | 19,070–2,054,500 | 38,601 | 114–19,848 | 46,064–53,065 |
| 2 | 36,097 | 17,763–2,082,809 | 40,624 | 108–21,276 | 45,876–53,227 |
| 3 | 241 | 17,464–31,119 | 0 | 114–146 | 53,553–53,571 |
| 4 | 849 | 14,205–62,571 | 9,650 | 115–117 | 53,392–53,409 |
| 5 | 989 | 13,444–69,500 | 7,978 | 111–2,960 | 52,612–53,492 |

Total: 73,761 points. All throttle values are zero; no throttle exceeds 1000.
No positive voltages below 1000 and no fractional sensor-channel rows were found.
These ranges are consistent with raw units; no clear mixed-scale evidence was
found. Zero throttle cannot establish its historic scale. Small speed/current
values can be legitimate raw readings, so range checks cannot prove provenance.
No migration is proposed and no existing records were changed. Any later migration
needs original CSV/provenance evidence and an explicitly reviewed per-run plan.

## Frontend coordination and validation

Keep display conversions exactly once for telemetry and analytics, including
average/max speed. `duration_seconds` is already seconds and must not be divided
by 1000 again; its meaning is now telemetry span even when ended_at is absent.
CSV consumers must use raw-unit headers rather than infer display units.

`python -m unittest discover -s tests -v` runs isolated SQLite tests (no configured
database access). They cover the supplied raw values, import/storage/response/
analytics/export round trip, tick duration independent of wall-clock timestamps,
selected fields and OpenAPI units, null statistics, single-point duration,
throttle bounds, boot resets, duplicate ticks, and rollover rejection.
