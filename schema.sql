CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE teams (
    team_id BIGSERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL
);

CREATE TABLE cars (
    car_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    year_created SMALLINT NOT NULL CHECK (year_created >= 1886),
    team_id BIGINT NOT NULL,
    CONSTRAINT cars_team_id_fkey
        FOREIGN KEY (team_id)
        REFERENCES teams(team_id)
        ON DELETE RESTRICT
);

CREATE TABLE drivers (
    driver_id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);

CREATE TABLE driver_team_history (
    history_id BIGSERIAL PRIMARY KEY,
    driver_id BIGINT NOT NULL,
    team_id BIGINT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,

    CONSTRAINT driver_team_history_driver_id_fkey
        FOREIGN KEY (driver_id)
        REFERENCES drivers(driver_id)
        ON DELETE CASCADE,

    CONSTRAINT driver_team_history_team_id_fkey
        FOREIGN KEY (team_id)
        REFERENCES teams(team_id)
        ON DELETE RESTRICT,

    CONSTRAINT driver_team_history_dates_check
        CHECK (ended_at IS NULL OR ended_at > started_at),

    CONSTRAINT driver_team_history_no_overlap
        EXCLUDE USING gist (
            driver_id WITH =,
            tstzrange(
                started_at,
                COALESCE(ended_at, 'infinity'::timestamptz),
                '[)'
            ) WITH &&
        )
);

CREATE TABLE locations (
    location_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500)
);

CREATE TABLE runs (
    run_id BIGSERIAL PRIMARY KEY,
    car_id BIGINT NOT NULL,
    location_id BIGINT NOT NULL,
    driver_id BIGINT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    notes TEXT,
    date_created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT runs_car_id_fkey
        FOREIGN KEY (car_id)
        REFERENCES cars(car_id)
        ON DELETE RESTRICT,

    CONSTRAINT runs_location_id_fkey
        FOREIGN KEY (location_id)
        REFERENCES locations(location_id)
        ON DELETE RESTRICT,

    CONSTRAINT runs_driver_id_fkey
        FOREIGN KEY (driver_id)
        REFERENCES drivers(driver_id)
        ON DELETE RESTRICT,

    CONSTRAINT runs_dates_check
        CHECK (ended_at IS NULL OR ended_at > started_at)
);

CREATE TABLE telemetry (
    run_id BIGINT NOT NULL,
    tick BIGINT NOT NULL,
    throttle REAL,
    speed REAL,
    current REAL,
    voltage REAL,

    CONSTRAINT telemetry_pkey
        PRIMARY KEY (run_id, tick),

    CONSTRAINT telemetry_run_id_fkey
        FOREIGN KEY (run_id)
        REFERENCES runs(run_id)
        ON DELETE CASCADE,

    CONSTRAINT telemetry_tick_check
        CHECK (tick >= 0),

    CONSTRAINT telemetry_throttle_check
        CHECK (throttle IS NULL OR throttle >= 0),

    CONSTRAINT telemetry_speed_check
        CHECK (speed IS NULL OR speed >= 0),

    CONSTRAINT telemetry_current_check
        CHECK (current IS NULL OR current >= 0),

    CONSTRAINT telemetry_voltage_check
        CHECK (voltage IS NULL OR voltage >= 0)
);