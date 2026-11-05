# settings

## Purpose
Environment-specific Django settings for local development and Railway deployment.

## Contents
- `base.py`: shared defaults.
- `dev.py`: local development overrides.
- `prod.py`: environment-variable-driven production settings.

## Inputs/Outputs
- Inputs: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `ACTIVE_SIMULATION_BACKEND`.
- Outputs: Django settings values consumed at process startup.

## Depends on
- Django settings system.
- WhiteNoise for static files.

## Used by
- Django runtime and management commands.
