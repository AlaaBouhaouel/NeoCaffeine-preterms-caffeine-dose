# tests

## Purpose
Pytest suites for webapp validation matrix, API success paths, and backend contract behavior.

## Contents
- `conftest.py`: Django setup and shared fixtures.
- `test_api_validation_matrix.py`: endpoint validation and error/status coverage.
- `test_api_success_paths.py`: end-to-end success flow checks.
- `test_backend_contract_demo.py`: SimulationBackend contract checks on demo backend.

## Inputs/Outputs
- Inputs: webapp Django settings and API endpoints.
- Outputs: pass/fail signals validating contract compliance.

## Depends on
- Django test client.
- Demo backend and runtime layer.

## Used by
- Local verification before merge.
