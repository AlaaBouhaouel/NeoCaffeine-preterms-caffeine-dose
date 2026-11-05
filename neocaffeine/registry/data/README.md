# data

## Purpose
The registry data: every population value, documented equation, prior, bound, threshold and rule used by NeoCaffeine, with its source. All values are written by hand by Ala; the code only reads these files. `null` means empty.

## Contents
- `registry_meta.yaml`: registry `version` and `date`.
- `CHANGELOG.md`: one section per registry version.
- `pk_models.yaml`: `models` with the five population PK models (`thomson_1996`, `falcao_1997`, `charles_2008`, `gao_2020`, `engbers_2021`).
- `dosing.yaml`: citrate-to-base factor, dosing-weight rule, oral bioavailability, oral absorption rate.
- `effect.yaml`: `models` with the `hill` effect model and its `hill_coefficient`.
- `maturity.yaml`: entries of the maturity module (none yet).
- `baseline.yaml`: `models` with the `maturity_exponential` design assumption; pre-dose window definition; population fallback.
- `priors.yaml`: CL and V variability per PK model; Emax, EC50 and beta_M population values and variabilities; clearance drift.
- `bounds.yaml`: concentration bounds; heart-rate flag threshold.
- `events.yaml`: event-definition version; apnea, bradycardia and desaturation definitions; event overlap rule.
- `observation.yaml`: assay error; default detection limit; valid-time exclusions.
- `validation_ranges.yaml`: ranges for gestational age, weight, dose amount, blood level, event count, FiO2.
- `decision.yaml`: target effect fraction, safety exceedance probability, dosing interval, maximum dose, loading and maintenance dose rules, standard regimen.

### Entry kinds
The kind is recognised from the keys an entry holds.

| Kind | Recognised by | Value fields |
|---|---|---|
| Scalar | `value` | `value`, `unit` |
| Range | `minimum` | `minimum`, `maximum`, `unit` |
| Choice | its name (see below) | `value` (one option), `unit` |
| Formula | `equation` | `equation`, `symbols`; optional `coefficients` (scalar entries) |
| PK model | `structure` | `structure`, `clearance_equation`, `volume_equation` (formulas), `coefficients`, `residual_error` |
| Event definition | `signal` | `signal`, `threshold`, `threshold_unit`, `min_duration`, `max_duration`, `duration_unit`, `counts_toward_N` |
| Fallback | `rate` | `rate`, `rate_unit`, `reported_maturity`, `reported_maturity_unit` |
| Exclusion | `enabled` | `enabled`, `value`, `unit` |
| Structural | `entry_type: structural` | `meaning` only |
| Design assumption | `entry_type: design_assumption` | `equation`, `symbols`, `meaning`, `rationale`, `citations`; tier fixed at C, no population |

A map that matches none of these is a group of entries (for example `models`, `clearance_variability`, `signal_artifact`).

Choice options:
- `dosing.dosing_weight_rule`: `birth_weight`, `latest_weight_on_or_before_dose`.
- `events.event_overlap_rule`: `separate`, `merge_within_window` (then `merge_window` and `merge_window_unit` are required).

### Common fields of sourced entries
`meaning`, `evidence_tier` (A, B or C), `population` (`gestational_age`, `postnatal_age`, `weight`, each with `min`, `max`, `unit`), `citations`, `conflicts_with`, `conflict_note`.

A citation needs `authors`, `year`, `title`, `journal_or_source`, `location` (table, equation or page) and at least one of `doi`, `pmid`, `url`. `volume`, `issue`, `pages`, `notes` are optional.

### Rules
- Units are never empty; unitless quantities use `dimensionless`. Every unit is checked by pint.
- `not_reported` is allowed only in value fields, only for values a cited source did not estimate, and needs a `not_reported_note` key in the same entry. It loads, but a run that requires it stops with an error naming it.
- `conflicts_with` lists full entry names (for example `priors.clearance_variability.engbers_2021`); a filled list needs a `conflict_note`.
- A run only requires the selected PK, effect and baseline models; other models may stay empty.
- An empty `coefficients` or `signal_artifact` map counts as missing.

## Inputs/Outputs
- Inputs: written by hand by Ala.
- Outputs: read by `neocaffeine/registry/loader.py`.

## Depends on
Nothing.

## Used by
- `neocaffeine/registry/`
