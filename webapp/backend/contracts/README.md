# contracts

## Purpose
Holds canonical enum values and shared contract constants for backend/frontend consistency.

## Contents
- `schemas.py`: phases, event types, dose enums, support enums, and route/form enums.

## Inputs/Outputs
- Inputs: approved naming decisions.
- Outputs: reusable constants referenced by backend and API handlers.

## Depends on
- Product decisions recorded in docs and approvals.
- `neocaffeine.patient.vocabularies` for sex, breathing support, dose route and dose form values.

## Used by
- Demo backend and request validation layers.
