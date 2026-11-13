# demo

## Purpose
Implements a reproducible fake simulation backend for end-to-end webapp behavior before real model integration.

## Contents
- `demo_simulation_backend.py`: backend stub implementation.
- `generators.py`: placeholder (vital signs are generated in the browser, see `js/vitals-generator.js`).
- `updater.py`: the live demo model (proposal 06): caffeine concentration from the dose log (one compartment, IV bolus), hourly curve points, demo apnea rate, daily N prefill (seeded Poisson), daily estimator step (half the gap to the true value, SD x 0.6), suggested dose, confidence gate, safety share, 3D trajectory.
- `thresholds.py`: every `DEMO_*` constant of the live demo (demo values approved by Ala, never registry values).

## Inputs/Outputs
- Inputs: backend interface calls and persisted run snapshots.
- Outputs: plausible state transitions marked as demo data. On create, a patient record and a run with its own patient document are stored in one transaction; on state reads, `state.patient` is rebuilt from that document.

## Depends on
- `backend/interfaces/` contract.
- `backend/contracts/` enum constants.
- `backend/patient_bridge.py`, `patients/` and `runs/` repositories.

## Used by
- Active backend selector when `ACTIVE_SIMULATION_BACKEND=demo`.
