# migrations

## Purpose
Stores Django migrations for the run snapshot persistence schema.

## Contents
- Migration files generated from `runs.models`.

## Inputs/Outputs
- Inputs: model changes.
- Outputs: database schema updates.

## Depends on
- Django migration framework.

## Used by
- `python webapp/manage.py migrate` in deployment and local setup.
