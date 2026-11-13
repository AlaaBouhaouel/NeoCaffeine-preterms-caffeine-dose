# vendor

## Purpose
Stores third-party frontend libraries saved in the repository (vendored), so the app serves them itself and needs no CDN at runtime.

## Contents
- `uplot/`: uPlot 1.6.31 (MIT), the 2D monitor and concentration graphs.
- `plotly/`: plotly.js 2.35.2, gl3d bundle (MIT), the 3D convergence view.

## Inputs/Outputs
- Inputs: pinned release files downloaded from the npm packages `uplot@1.6.31` and `plotly.js-gl3d-dist-min@2.35.2`.
- Outputs: static resources loaded by the dashboard.

## Depends on
- Exact version pinning; to upgrade, replace the files and update the versions here.

## Used by
- `js/charts.js` (uPlot) and `js/convergence-3d.js` (plotly), loaded by `templates/dashboard.html`.
