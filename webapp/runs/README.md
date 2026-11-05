# runs

## Purpose
Persists simulation run snapshots in PostgreSQL with state versioning and retention metadata.

## Contents
- `models.py`: snapshot model.
- `repositories.py`: read/write/delete operations.
- `migrations/`: schema migrations.

## Inputs/Outputs
- Inputs: run IDs, state versions, and full state JSON objects.
- Outputs: persisted snapshots and retention cleanup results.

## Depends on
- Django ORM and configured database.

## Used by
- Backend implementations and API action handlers.
