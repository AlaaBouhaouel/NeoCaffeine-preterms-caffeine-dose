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
- Outputs: plausible state transitions marked as demo data.

## Depends on
- `backend/interfaces/` contract.
- `backend/contracts/` enum constants.

## Used by
- Active backend selector when `ACTIVE_SIMULATION_BACKEND=demo`.
