# webapp

## Purpose
Django web interface for NeoCaffeine, running as a public research demo and consuming simulation data only through the backend boundary.

## Contents
- `manage.py`: Django management entrypoint.
- `neocaffeine_web/`: Django project settings and root URLs.
- `simulator/`: pages, API handlers, templates, and static assets.
- `backend/`: simulation interface, selector, and demo backend.
- `patients/`: patient persistence (patient_id and covariates, shared by all runs of the patient).
- `runs/`: snapshot persistence models and repositories; each run holds its own patient document.
- `tests/`: webapp tests, run on Django's temporary test database (pytest-django), never on `db.sqlite3`.
- `docs/`: webapp-scoped contract and copy drafts.

## Inputs/Outputs
![Dashboard in dark mode](../docs/images/image.png)

- Inputs: backend state payloads, user interventions, and run identifiers.
- Outputs: landing page, simulator dashboard, and JSON API responses.

## Depends on
- Django, WhiteNoise, gunicorn (deployment), psycopg (PostgreSQL driver).
- SQLite locally; PostgreSQL in deployment environments (Railway, commands in `railway.json`).
- `neocaffeine.patient` and `neocaffeine.registry` (patient objects, validation ranges).
- uPlot for charts in simulator pages.

## Used by
- Clinicians and researchers reviewing virtual-infant simulations.
- Future backend implementation that plugs into the interface boundary.
