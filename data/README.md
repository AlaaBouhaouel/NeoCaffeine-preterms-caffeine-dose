# data

## Purpose
Local-only folder for real patient records and raw signal files. **No patient data is ever committed to this repository.** Everything in this folder is excluded by `.gitignore`, except this README.

## Contents
This README only, in the repository. Local files placed here are never tracked.

## Inputs/Outputs
- Inputs: real record files copied here locally.
- Outputs: none; files are read by the ingestion layer.

## Depends on
Nothing.

## Used by
- `neocaffeine/ingest/`: loads records from this folder into patient objects.
