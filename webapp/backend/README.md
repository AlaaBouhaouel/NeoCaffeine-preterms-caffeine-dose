# backend

## Purpose
Single simulation boundary for the web app, with an interface and selectable backend implementation.

## Contents
- `interfaces/`: abstract backend contract.
- `contracts/`: canonical enums and schema keys.
- `demo/`: deterministic demo backend behavior.
- `selectors.py`: active backend selection in one place.

## Inputs/Outputs
- Inputs: run actions from API handlers and current persisted state.
- Outputs: state envelopes and summaries in approved JSON shapes.

## Depends on
- Webapp run persistence layer.
- Approved API/state contract.

## Used by
- `simulator/views/api_*` handlers.
