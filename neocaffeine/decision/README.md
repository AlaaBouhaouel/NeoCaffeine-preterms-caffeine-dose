# decision

## Purpose
Turns the current estimate into a dose suggestion for clinician review. Computes the target concentration from the inverted Hill curve, clamped to the concentration bounds; the dose from CL, V and the caffeine already in the body; a safety check by sampling theta from its uncertainty; the confidence gate; and the output flags. Never doses on its own.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: theta_k, Sigma_k, current A(t), registry decision entries, run configuration (safety samples, dose rounding).
- Outputs: suggested dose, predicted concentration range, flags.

## Depends on
- `neocaffeine/models/`, `neocaffeine/registry/`

## Used by
- `neocaffeine/runner/`
- `webapp/`
