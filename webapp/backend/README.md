# backend

## Purpose
Single simulation boundary for the web app, with an interface and selectable backend implementation.

## Contents
- `interfaces/`: abstract backend contract.
- `contracts/`: canonical enums and schema keys.
- `demo/`: deterministic demo backend behavior.
- `selectors.py`: active backend selection in one place.
- `runtime.py`: backend-agnostic rule enforcement (state_version, phase, converged lock).
- `state_upgrade.py`: converts run states stored before daily N (`hour_gate`, `last_hour`, hourly diagnostics) to the daily-N shape when they are read, so older runs still load.
- `patient_bridge.py`: landing payload → `neocaffeine.patient.Patient` (covariates + initial context at birth); patient ↔ versioned JSON document; patient → dashboard `state.patient`; registry validation ranges loaded once per process.

## Inputs/Outputs
- Inputs: run actions from API handlers and current persisted state.
- Outputs: state envelopes and summaries in approved JSON shapes.

## Depends on
- Webapp persistence layer (`patients/`, `runs/`).
- `neocaffeine.patient` and `neocaffeine.registry`.
- Approved API/state contract.

## Used by
- `simulator/views/api_*` handlers.
