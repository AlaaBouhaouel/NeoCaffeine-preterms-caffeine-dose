# tests

## Purpose
pytest tests for the `neocaffeine` package. The folder layout mirrors the package: each package folder gets a matching test folder when its code is written.

## Contents
- `clock/`: tests for `neocaffeine/clock/`.
- `registry/`: tests for `neocaffeine/registry/`.
- `patient/`: tests for `neocaffeine/patient/`.

Conventions:
- Test files are named `test_<module>.py`.
- Test folders have no `__init__.py`; pytest runs with `--import-mode=importlib` (set in `pyproject.toml`) so mirrored file names do not collide.
- Run with `uv run pytest`.

## Inputs/Outputs
- Inputs: the `neocaffeine` package.
- Outputs: pass or fail results.

## Depends on
- `neocaffeine/`
- pytest (dev dependency group).

## Used by
Developers, before each commit.
