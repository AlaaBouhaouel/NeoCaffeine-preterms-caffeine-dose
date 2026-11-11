# tests

## Purpose
Pytest suites for webapp validation matrix, API success paths, backend contract behavior, and patient persistence. Every test runs on Django's temporary test database through pytest-django, never on `webapp/db.sqlite3`.

## Contents
- `conftest.py`: test database access and shared payload fixtures.
- `test_api_validation_matrix.py`: endpoint validation and error/status coverage, including `birth_time` and the package vocabularies.
- `test_api_success_paths.py`: end-to-end success flow checks.
- `test_backend_contract_demo.py`: SimulationBackend contract checks on demo backend.
- `test_patient_persistence.py`: patient record and per-run patient document stored on create; dashboard `state.patient` loaded from them; UTC birth time; range flags.

## Inputs/Outputs
- Inputs: webapp Django settings (`neocaffeine_web.settings.dev`, set in `pyproject.toml`) and API endpoints.
- Outputs: pass/fail signals validating contract compliance.

## Depends on
- pytest-django and the Django test client.
- Demo backend, runtime layer, `patients/` and `runs/` apps.

## Used by
- Local verification before merge (`uv run pytest`, which also runs the package tests in `tests/`).
