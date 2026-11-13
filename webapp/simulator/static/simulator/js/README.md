# js

## Purpose
Client-side logic for clock control, API calls, state handling, tooltips, and charts.

## Contents
- `api-client.js`: HTTP client helpers.
- `state-store.js`: state and version tracking.
- `clock-controller.js`: browser-side play/pause/speed loop.
- `dashboard-ui.js`: panel rendering and interaction wiring.
- `charts-uplot.js`: uPlot chart integration.
- `tooltips.js`: hover/tap info behavior.
- `theme-toggle.js`: light/dark switch for every `.theme-toggle` button; first visit follows the OS setting, a press is remembered in localStorage (`neocaffeine-theme`); fires `neocaffeine:themechange`.
- `landing.js`: landing form, run creation, resume, and the animated motif (colours read from theme tokens).

## Inputs/Outputs
- Inputs: user actions and server state responses.
- Outputs: API requests and updated DOM state.

## Depends on
- Approved API contract and template markup.

## Used by
- `dashboard.html` and related partials.
