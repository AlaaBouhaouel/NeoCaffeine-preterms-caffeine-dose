# patient

## Purpose
One infant. Holds the covariates (gestational age, birth time, birth weight, weight over time, sex), the dose log, blood levels, the context log (FiO2, support mode), references to raw signals, the detected event list and the daily records (one per 24 h observation day). Logs are append-only: every entry has its own UUID, and a correction is a new entry that supersedes an earlier one. Postnatal and postmenstrual age are computed from the clock, never stored. No personal data is held.

Every entry has an event time (hours since birth) and a recording sequence number (the order it was added, one counter across all logs, the audit order). Chronology in event time is enforced on original entries only; corrections may carry an earlier time. A change of event definition adds records under the new version next to the old ones; the current view selects by version.

Two validation levels: impossible values (for example a negative weight, FiO2 outside 0.21 to 1.0) raise `DefinitionalError`; values outside the registry validation range are flagged `out_of_validation_range`; an empty registry range is flagged `range_unchecked` and never blocks adding data. An out-of-range observation (blood level, daily record) excludes its observation day from estimation.

## Contents
- `patient_errors.py`: `PatientError` (a `ValueError`) and its subclasses.
- `vocabularies.py`: `Sex`, `Route`, `SaltForm`, `SampleType`, `SupportMode`, `SignalType`, `EventType`.
- `definitional_checks.py`: shared checks for impossible values.
- `covariates.py`: `Covariates` (gestational age in days, birth time in UTC, birth weight in grams, sex, patient UUID) and `gestational_age_days_from(weeks, days)`.
- `log_entry.py`: `Correction` (supersedes, recorded at in UTC, reason) and `new_entry_id`.
- `weight_entry.py`, `dose_entry.py`, `blood_level_entry.py`, `context_entry.py`, `signal_reference.py`, `detected_event.py`, `daily_record.py`, `baseline_record.py`: one entry type each.
- `append_only_log.py`: `AppendOnlyLog` (chronology, duplicates, corrections, current view) and `RecordedEntry`.
- `validation_flag.py`: `FlagKind` and `ValidationFlag`.
- `range_validation.py`: `ValidationRanges` (built from the registry) converts each range to the field's unit with pint.
- `patient.py`: `Patient`: one `add_…` method per log, current views, weight at a time (birth weight before the first measurement, then carried forward), ages through `clock/`, flags and excluded days.
- `patient_serialization.py`: patient to and from a JSON-ready map with `schema_version` 2 (daily records); a version-1 file loads only if its `hourly_records` list is empty; real-world times in ISO 8601 UTC, event times in hours since birth; loading re-validates every entry.
- `patient_file.py`: `write_patient_file` and `read_patient_file`, one `<patient_id>.json` per patient. Real patients go in `data/`, virtual patients in `results/virtual/`.

## Inputs/Outputs
- Inputs: covariates, log entries, `ValidationRanges` from the registry, patient files.
- Outputs: the patient object, current views of its logs, age helpers, validation flags, excluded days, patient files.

## Depends on
- `neocaffeine/clock/`
- `neocaffeine/registry/` (validation ranges, pint unit registry)

## Used by
- `neocaffeine/ingest/`, `neocaffeine/features/`, `neocaffeine/simulator/`, `neocaffeine/estimator/`, `neocaffeine/decision/`, `neocaffeine/runner/`
