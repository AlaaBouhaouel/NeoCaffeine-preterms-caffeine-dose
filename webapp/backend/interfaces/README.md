# interfaces

## Purpose
Defines the backend protocol consumed by all views and frontend flows.

## Contents
- `simulation_backend.py`: `SimulationBackend` protocol and payload aliases.

## Inputs/Outputs
- Inputs: typed method parameters for run creation, advancing, interventions, and summary retrieval.
- Outputs: state and summary envelopes.

## Depends on
- Approved endpoint and state contract.

## Used by
- Backend selector.
- Demo backend implementation.
- Future real backend implementation.
