# demo

## Purpose
Implements a reproducible fake simulation backend for end-to-end webapp behavior before real model integration.

## Contents
- `demo_simulation_backend.py`: backend stub implementation.
- `generators.py`: trace/event generation helpers.
- `updater.py`: state update and estimator placeholders.
- `thresholds.py`: demo-only thresholds.

## Inputs/Outputs
- Inputs: backend interface calls and persisted run snapshots.
- Outputs: plausible state transitions marked as demo data. On create, a patient record and a run with its own patient document are stored in one transaction; on state reads, `state.patient` is rebuilt from that document.

## Depends on
- `backend/interfaces/` contract.
- `backend/contracts/` enum constants.
- `backend/patient_bridge.py`, `patients/` and `runs/` repositories.

## Used by
- Active backend selector when `ACTIVE_SIMULATION_BACKEND=demo`.
