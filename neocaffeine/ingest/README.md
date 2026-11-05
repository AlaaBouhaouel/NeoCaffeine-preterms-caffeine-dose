# ingest

## Purpose
Loads real patient records into patient objects, converting real timestamps to hours since birth. Used in real-data mode only. The record format is decided later.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: record files from the local `data/` folder.
- Outputs: patient objects.

## Depends on
- `neocaffeine/patient/`, `neocaffeine/clock/`, `neocaffeine/registry/`

## Used by
- `neocaffeine/runner/`
