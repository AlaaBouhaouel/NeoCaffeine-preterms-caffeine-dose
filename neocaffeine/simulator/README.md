# simulator

## Purpose
Virtual infants with known true parameters, for validation before any real data. Simulates concentrations under a dosing schedule and generates apnea events, blood levels with assay error, artifacts and missing periods, packaged as patient objects.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: registry entries, run configuration (random seed), dosing schedule.
- Outputs: patient objects plus their true parameters.

## Depends on
- `neocaffeine/models/`, `neocaffeine/patient/`, `neocaffeine/clock/`, `neocaffeine/registry/`

## Used by
- `neocaffeine/runner/`, `neocaffeine/evaluation/`
