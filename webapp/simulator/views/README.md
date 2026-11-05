# views

## Purpose
Contains request handlers for landing/dashboard pages and run APIs.

## Contents
- `landing.py`, `dashboard.py`: HTML page views.
- `api_runs.py`: run creation endpoint.
- `api_state.py`: state and summary endpoints.
- `api_actions.py`: advance and N-submission endpoints.

## Inputs/Outputs
- Inputs: HTTP requests and validated JSON payloads.
- Outputs: rendered templates or JSON envelopes.

## Depends on
- Django view and URL dispatching.
- Backend selector and interface.

## Used by
- `simulator/urls.py`.
