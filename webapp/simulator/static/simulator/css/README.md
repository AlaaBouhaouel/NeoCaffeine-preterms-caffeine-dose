# css

## Purpose
Stylesheet files for landing and dashboard layouts.

## Contents
- `theme.css`: colour tokens (`--color-*`) for the dark theme (original palette) and the light theme (`<html data-theme="light">`). The other stylesheets use only these tokens, never colour literals.
- `base.css`: shared primitives.
- `landing.css`: landing-specific design.
- `dashboard.css`: dense monitor-style dashboard.

## Inputs/Outputs
- Inputs: approved color/font/layout decisions.
- Outputs: rendered visual styling in browser.

## Depends on
- Template DOM structure.

## Used by
- Landing and dashboard pages.
