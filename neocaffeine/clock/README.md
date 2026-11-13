# clock

## Purpose
Time base of the project. Inside the model, time is one number: hours since birth. This folder converts timezone-aware UTC timestamps to hours since birth and back, gives the hour index k (hour k is the half-open interval [k, k+1)) and the observation day index d (day d is [24d, 24d+24), the window of one N), and provides two clocks:
- a data clock, which follows real timestamps;
- a simulation clock, which advances instantly from event to event.

Rules: timestamps must be timezone-aware UTC (naive or other zones are rejected, including zones that merely sit at offset zero, such as Europe/London in winter) and are truncated to whole seconds. Anything before birth is rejected. Values are plain floats with the unit in the name; conversion to pint happens only where a value enters a registry formula.

## Contents
- `clock_errors.py`: `ClockError` (a `ValueError`) and its subclasses `NaiveTimestampError`, `NonUtcTimestampError`, `BeforeBirthError`, `ClockMovedBackwardsError`, `UnknownTimezoneError`.
- `utc_check.py`: `require_utc` validates a timestamp and truncates it to whole seconds.
- `time_axis.py`: `hours_since_birth`, `timestamp_from_hours` (rounds to the nearest second), `hour_index`, `hour_bounds`, `day_index`, `day_bounds`, `require_not_before_birth`.
- `ages.py`: `day_of_life` (first day is 1), `postnatal_age_days`, `postmenstrual_age_days`, `postmenstrual_age_weeks`.
- `local_time.py`: `to_local_time`, using the IANA zone name from the run configuration.
- `clock.py`: the `Clock` protocol (`current_hours`, `advance_to`).
- `real_clock.py`: `RealClock`, starts when the system starts for an infant and is advanced by the runner to the latest data timestamp.
- `simulated_clock.py`: `SimulatedClock`, advances instantly for virtual infants.

Both clocks reject moving backwards; advancing to the current time is a no-op.

## Inputs/Outputs
- Inputs: birth time (UTC), timestamps (UTC), hours since birth, gestational age in days, display time-zone name.
- Outputs: hours since birth, hour index k, hour bounds, day index d, day bounds, ages, UTC and local timestamps.

## Depends on
- Python standard library (`datetime`, `zoneinfo`), with `tzdata` providing the time-zone database.

## Used by
- `neocaffeine/patient/`, `neocaffeine/ingest/`, `neocaffeine/simulator/`, `neocaffeine/runner/`
- `webapp/`
