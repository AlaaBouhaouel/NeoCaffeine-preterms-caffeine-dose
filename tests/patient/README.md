# patient (tests)

## Purpose
Tests for `neocaffeine/patient/`.

## Contents
- `conftest.py`: fixtures. A test infant, empty validation ranges (as in an unfilled registry), the real registry validation ranges, and validation ranges filled with arbitrary test placeholder limits (not physiological values).
- `test_covariates.py`: required covariates, impossible values, UTC birth time, immutability, weeks-plus-days helper.
- `test_entries.py`: impossible values for every entry type, FiO2 0.21 to 1.0, below-detection-limit rules, hours without valid time.
- `test_append_only_log.py`: chronology of originals, duplicates, corrections (earlier times, chains, double supersede, unknown entry), recording sequence, coexisting definition versions.
- `test_range_validation.py`: `range_unchecked` with an empty registry, every real registry range usable, out-of-range flags and excluded hours, corrections lifting exclusion, per-event-type count ranges, pint conversion, wrong-dimension units, covariate flags.
- `test_patient.py`: weight carry-forward, ages, baseline records per version, wrong entry type.
- `test_patient_file.py`: JSON round trip, file name, ISO 8601 for real-world times and hours for event times, re-validation on load, schema version, unknown keys, missing file.

## Inputs/Outputs
- Inputs: the patient package.
- Outputs: pass or fail results.

## Depends on
- `neocaffeine/patient/`, `neocaffeine/registry/`, `neocaffeine/clock/`
- pytest

## Used by
Developers, before each commit.
