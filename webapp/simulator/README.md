# simulator

## Purpose
Owns landing and dashboard experiences plus HTTP APIs for simulation run interaction.

## Contents
- `views/`: page and API handlers.
- `templates/`: HTML templates and panel partials.
- `static/`: CSS, JavaScript, and vendor assets.
- `urls.py`: app-level route definitions.

## Inputs/Outputs
- Inputs: HTTP requests, run IDs, action payloads.
- Outputs: rendered pages and JSON responses.

## Depends on
- `backend/` boundary.
- `runs/` persistence.

## Used by
- Root URL routing in `neocaffeine_web/urls.py`.
