# registry (tests)

## Purpose
Tests for `neocaffeine/registry/`.

## Contents
- `conftest.py`: fixtures. Copies of the real empty registry, and a copy filled with placeholder test values (`test fixture placeholder`, `1.0`, `dimensionless`, tier `C`, year `2000`). These placeholders exist only in temporary test folders; the real registry files stay empty.
- `test_loader.py`: the shipped empty registry loads; all five PK models present; lookup by full name; design assumptions listed; no reference maturity; missing file and unknown conflict names rejected.
- `test_entry_parser.py`: unknown keys, wrong types, invalid tiers, unknown units, `not_reported` without a note, choices outside their options, structural and design-assumption schemas.
- `test_completeness.py`: the empty registry refuses to run and lists every missing item; only selected models required; empty coefficients missing; structural and design-assumption rules; a filled registry passes; `not_reported` stops a run only when required; merge-window condition; citation identifier, optional fields and conflict note.

## Inputs/Outputs
- Inputs: the registry package and its data files.
- Outputs: pass or fail results.

## Depends on
- `neocaffeine/registry/`
- pytest, ruamel.yaml

## Used by
Developers, before each commit.
