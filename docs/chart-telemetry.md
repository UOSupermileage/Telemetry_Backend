# Fetching telemetry for charts

Use the existing `GET /telemetry/data` endpoint with `max_points` to request a
bounded sample spanning the entire run, rather than the first page of readings:

```text
/telemetry/data?run_id=4&fields=speed&fields=current&max_points=800
```

On chart zoom or pan, request the visible tick range with the same point budget:

```text
/telemetry/data?run_id=4&fields=speed&fields=current&start_tick=20000&end_tick=30000&max_points=800
```

Tick bounds are inclusive milliseconds since boot. Response format remains an
array of objects with `tick` and the requested fields. Values remain raw sensor
units: apply frontend display conversions once.

`max_points` accepts 2–10000. When there are more matching rows, the database
selects that many original readings spread evenly by row position, including
the first and last matching points. With fewer rows, all matching rows are
returned. A single matching row returns one point. No matching rows returns the
existing 404 response. Irregular sampling means spacing in time can vary.

In chart mode, `max_points` overrides `limit` and `offset` must be zero (otherwise
400). Omitting `max_points` retains the existing `offset`/`limit` pagination.
Sampling runs in one database statement and only selected points are transferred
to the backend; the database still scans the matching range to rank rows.

The frontend chooses the budget based on chart width; 800 is an example. Debounce
zoom/pan fetches, cancel superseded requests, and replace the chart data when the
latest response arrives. Zooming into a smaller tick interval increases detail
without increasing the response size. Resetting zoom should omit the tick bounds.

Uniform sampling can omit short spikes or null gaps. Use analytics for exact
statistics, and zoom in or use paginated raw readings for closer inspection.
Do not compute run statistics from chart samples. Database storage, analytics,
and CSV exports continue using full-resolution data.
