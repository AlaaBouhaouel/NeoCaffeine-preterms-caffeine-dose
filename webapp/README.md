# webapp

## Purpose
Django web interface for NeoCaffeine, running as a public research demo and consuming simulation data only through the backend boundary.

## Contents
- `manage.py`: Django management entrypoint.
- `neocaffeine_web/`: Django project settings and root URLs.
- `simulator/`: pages, API handlers, templates, and static assets.
- `backend/`: simulation interface, selector, and demo backend.
- `runs/`: snapshot persistence models and repositories.
- `docs/`: webapp-scoped contract and copy drafts.

## Inputs/Outputs
- Inputs: backend state payloads, user interventions, and run identifiers.
- Outputs: landing page, simulator dashboard, and JSON API responses.

## Depends on
- Django.
- PostgreSQL in deployment environments.
- uPlot for charts in simulator pages.

## Used by
- Clinicians and researchers reviewing virtual-infant simulations.
- Future backend implementation that plugs into the interface boundary.
