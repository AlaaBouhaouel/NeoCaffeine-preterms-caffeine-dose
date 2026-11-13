# css

## Purpose
Stylesheet files for landing and dashboard layouts.

## Contents
- `theme.css`: colour tokens (`--color-*`) for the dark theme (original palette) and the light theme (`<html data-theme="light">`). The other stylesheets use only these tokens, never colour literals.
- `base.css`: shared primitives.
- `landing.css`: landing-specific design.
- `dashboard.css`: dense monitor-style dashboard.
- `mobile.css`: phone layout (proposal 08) for both pages; every rule is inside one `@media (max-width: 760px)` block, so wider screens ignore it. Loaded last. Pages scroll in one column; dashboard order: dose card, N card, monitor, estimator, 3D, clinician actions, then Patient/Run/Counts behind the "Patient and run details" button.
- `user-guide.css`: guided tour overlay, highlight rings, step cards (docked at the bottom below 640 px), ? button.

## Inputs/Outputs
- Inputs: approved color/font/layout decisions.
- Outputs: rendered visual styling in browser.

## Depends on
- Template DOM structure.

## Used by
- Landing and dashboard pages.
