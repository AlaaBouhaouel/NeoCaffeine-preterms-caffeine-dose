# js

## Purpose
Client-side logic for clock control, API calls, state handling, tooltips, and charts.

## Contents
- `api-client.js`: HTTP client helpers.
- `state-store.js`: state and version tracking.
- `clock-controller.js`: browser-side play/pause/speed loop; one `advance` call per real second (graphs interpolate in between).
- `dashboard-ui.js`: panel rendering and interaction wiring.
- `vitals-generator.js`: DEMO heart rate, SpO2 and respiration generated in the browser from the run seed and simulated time (1 sample per simulated minute), with apnea episodes at the server's demo apnea rate; never stored.
- `charts.js`: uPlot graphs: the three vital-sign trends (last 6 simulated hours, about 10 frames per second) and the caffeine concentration curve (estimate, uncertainty band, true curve when "True values" is ticked, dose markers); fills the vital tiles.
- `convergence-3d.js`: plotly 3D view of the daily estimate path for the two parameters chosen in the X/Y dropdowns; true value shown when "True values" is ticked.
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
