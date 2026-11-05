# patient

## Purpose
One infant. Holds the covariates (gestational age, birth time, birth weight, weight over time, sex), the dose log, blood levels, the context log (FiO2, support mode), references to raw signals, the detected event list and the hourly records. Logs are append-only: every entry has its own UUID, and a correction is a new entry that supersedes an earlier one. Postnatal and postmenstrual age are computed from the clock, never stored. No personal data is held.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: covariates and log entries.
- Outputs: the patient object, current views of its logs, postnatal and postmenstrual age helpers, validation flags.

## Depends on
- `neocaffeine/clock/`
- `neocaffeine/registry/` (validation ranges)

## Used by
- `neocaffeine/ingest/`, `neocaffeine/features/`, `neocaffeine/simulator/`, `neocaffeine/estimator/`, `neocaffeine/decision/`, `neocaffeine/runner/`
