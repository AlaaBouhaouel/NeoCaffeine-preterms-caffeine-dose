# settings

## Purpose
Environment-specific Django settings for local development and Railway deployment.

## Contents
- `base.py`: shared defaults; installed apps (`patients`, `runs`, `simulator`); `STORAGES` with WhiteNoise compressed manifest storage for static files.
- `dev.py`: local development and test overrides (SQLite, plain static storage so no collectstatic manifest is needed).
- `prod.py`: environment-variable-driven production settings (PostgreSQL from `DATABASE_URL`).

Railway commands live in `railway.json` at the repository root; they pass `--settings=neocaffeine_web.settings.prod` because `manage.py` defaults to `dev`.

## Inputs/Outputs
- Inputs: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `ACTIVE_SIMULATION_BACKEND`.
- Outputs: Django settings values consumed at process startup.

## Depends on
- Django settings system.
- WhiteNoise for static files.

## Used by
- Django runtime and management commands.
