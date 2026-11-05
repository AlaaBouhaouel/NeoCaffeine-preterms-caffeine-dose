# config

## Purpose
Holds the run configuration: the numerical and procedural settings of a run that are not physiological. Physiological values, formulas and thresholds live in the parameter registry, never here.

## Contents
No files yet.

## Inputs/Outputs
- Inputs: none; the files are written by hand.
- Outputs: YAML settings read at the start of a run: selected pharmacokinetic model name, mode (virtual-infant or real-data), random seed, Newton's method settings (damping, tolerance, maximum iterations, handling of a non-positive-definite Hessian), barrier form and strength, number of safety samples, dose rounding.

## Depends on
Nothing.

## Used by
- `neocaffeine/registry/`: the selected model decides which registry entries are required.
- `neocaffeine/estimator/`, `neocaffeine/decision/`, `neocaffeine/runner/`, `neocaffeine/simulator/`.
