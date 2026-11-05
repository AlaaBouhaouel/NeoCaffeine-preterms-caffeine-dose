# templates

## Purpose
HTML templates for the landing page, simulator dashboard, and shared layout.

## Contents
- `base.html`: shared page shell.
- `landing.html`: entry page.
- `dashboard.html`: simulator page.
- `partials/`: panel and shared fragments.

## Inputs/Outputs
- Inputs: template context values such as `run_id` and UI flags.
- Outputs: rendered HTML.

## Depends on
- Django templating engine.

## Used by
- Page views in `simulator/views/`.
