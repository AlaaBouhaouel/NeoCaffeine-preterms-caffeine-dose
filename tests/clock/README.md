# clock (tests)

## Purpose
Tests for `neocaffeine/clock/`.

## Contents
- `test_utc_check.py`: naive, non-UTC and offset-zero zones rejected; UTC spellings accepted; microseconds truncated.
- `test_time_axis.py`: timestamp ↔ hours round trip, hour boundaries, rounding, before-birth rejection.
- `test_ages.py`: day of life, continuous postnatal age, postmenstrual age, before-birth rejection.
- `test_local_time.py`: UTC to a named zone, unknown zone name, naive timestamp.
- `test_real_clock.py`: start, forward, no-op, backwards rejected, timestamp advance, protocol fit.
- `test_simulated_clock.py`: start, instant jump, no-op, backwards rejected, protocol fit.

Values in these tests are arbitrary dates and times, not physiological values.

## Inputs/Outputs
- Inputs: the clock package.
- Outputs: pass or fail results.

## Depends on
- `neocaffeine/clock/`
- pytest

## Used by
Developers, before each commit.
