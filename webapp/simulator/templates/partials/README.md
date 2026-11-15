# partials

## Purpose
Reusable dashboard panel fragments and shared UI snippets.

## Contents
- Monitor, pharmacology, estimator, patient-file, decision panels.
- Footer notice and demo-data badge fragments.
- `intro.html`: three-card NeoCaffeine introduction (the problem, today's treatment, our solution), included in `landing.html` as a hidden overlay (opened by `js/intro.js`); cards switch with hidden radio buttons. Built from `templates/neocaffeine-intro.html`.

## Inputs/Outputs
- Inputs: panel data from state payloads.
- Outputs: reusable HTML blocks inserted into dashboard template.

## Depends on
- Dashboard template structure.

## Used by
- `simulator/templates/dashboard.html`.
