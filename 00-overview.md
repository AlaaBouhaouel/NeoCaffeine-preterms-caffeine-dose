# NeoCaffeine

**A gray-box simulator that estimates each preterm infant's hidden caffeine response and suggests individualized doses for apnea of prematurity.**

> **Status:** proof of concept, under active development.
> **Not a medical device.** NeoCaffeine is a research tool. Its outputs are suggestions for review by qualified clinicians and must never be used to dose a patient directly.

Author: Ala Bouhaouel, King Fahd University of Petroleum and Minerals (KFUPM), Dhahran, Saudi Arabia.
Date: Nov 2026
---

## Table of contents

1. [Overview](#1-overview)
2. [Glossary](#2-glossary)
3. [How the system works, in one page](#3-how-the-system-works-in-one-page)
4. [Technical design](#4-technical-design)
   - 4.1 [Time model](#41-time-model)
   - 4.2 [Variable roles](#42-variable-roles)
   - 4.3 [The model chain](#43-the-model-chain)
   - 4.4 [Observations](#44-observations)
   - 4.5 [The estimator](#45-the-estimator)
   - 4.6 [What can and cannot be learned](#46-what-can-and-cannot-be-learned)
   - 4.7 [The dose decision](#47-the-dose-decision)
   - 4.8 [Parameter registry](#48-parameter-registry)
   - 4.9 [Run configuration](#49-run-configuration)
   - 4.10 [Modes and validation](#410-modes-and-validation)
5. [Repository structure](#5-repository-structure)
6. [Data policy](#6-data-policy)
7. [Limitations](#7-limitations)
8. [Roadmap](#8-roadmap)
9. [References](#9-references)

## Structure of the folder
neocaffeine/
├── README.md
├── requirements.txt
├── neocaffeine/
│   ├── __init__.py
│   ├── constants.py
│   ├── patient.py
│   ├── pk.py
│   ├── efficacy.py
│   ├── toxicity.py
│   ├── events.py
│   ├── biomarkers.py
│   ├── devices.py
│   ├── dosing.py
│   ├── scenario.py
│   └── metrics.py
└── tests/
    └── __init__.py

---

## 1. Overview

### The clinical problem

**Apnea of prematurity** is a pause in breathing in babies born too early, caused mainly by an immature brainstem, the part of the brain that controls breathing automatically. It affects nearly all infants born before 29 weeks of gestation, and the pauses are often followed by drops in heart rate and blood oxygen [1, 2].

**Caffeine citrate** has been the first-line treatment for decades: it stimulates breathing and improves long-term outcomes [3, 4]. In most neonatal intensive care units, it is given by a standard regimen scaled to body weight [5].

But infants respond very differently:

- Some keep having apneas even at concentrations considered therapeutic [6], while others reach levels associated with toxicity on standard doses [7].
- The same infant changes over time: caffeine clearance (how fast the body removes it) rises about fourfold in the first month of life [8], so a fixed dose delivers less and less exposure [9].

A one-size-fits-all regimen therefore over-treats some infants and under-treats others.

### What NeoCaffeine does

NeoCaffeine treats each infant as a system with **hidden properties** (how fast they remove caffeine, how sensitive they are to it, how their breathing matures) and estimates those properties **hour by hour from the infant's own data**: apnea events, blood caffeine levels when available, and a maturity signal derived from brain and respiratory recordings. With the estimated properties, it computes which concentration this infant needs and which dose reaches it, then hands that suggestion to a clinician.

### Where the ideas come from

- **Observer-based estimation:** recovering hidden states of a body system from cheap measurements, as in Bhatti's estimator for an epileptic seizure model [10].
- **In silico testing:** the UVA/Padova Type 1 Diabetes Simulator showed that a validated virtual population can serve as a testbed for dosing algorithms before clinical studies [11].
- **Functional brain age:** maturity of the preterm brain can be estimated from its electrical activity [12].

### What it is not

- It is **not a neural network.** There is not enough clinical data to train one, and its internal numbers would have no physical meaning. NeoCaffeine uses known physiological equations with a small number of unknown, interpretable parameters (a gray-box model, see the glossary).
- It is **not autonomous.** Every output is a suggestion for clinical review.

---

## 2. Glossary

| Term | Meaning |
|---|---|
| **Apnea** | A pause in breathing. Exact detection criteria are defined in the parameter registry. |
| **Bradycardia** | A drop in heart rate below a defined threshold. |
| **Desaturation** | A drop in blood oxygen saturation (SpO2) below a defined threshold. |
| **GA (gestational age)** | Age of the pregnancy at birth, in weeks. |
| **PNA (postnatal age)** | Time since birth. |
| **PMA (postmenstrual age)** | GA plus PNA. The infant's total age counted from the start of pregnancy. |
| **SpO2** | Peripheral oxygen saturation: the percentage of hemoglobin carrying oxygen, measured by a pulse oximeter on the hand or foot. |
| **FiO2** | Fraction of inspired oxygen: the share of oxygen in the gas the infant breathes, set by clinicians (room air is about 21 percent). |
| **Pharmacokinetics** | What the body does to the drug: how it enters, spreads, and leaves. |
| **Pharmacodynamics** | What the drug does to the body: how concentration produces an effect. |
| **Concentration (C)** | Amount of caffeine per liter of blood (mg/L). |
| **Clearance (CL)** | Volume of blood fully cleaned of caffeine per hour (L/h). The "size of the leak." |
| **Volume of distribution (V)** | The apparent volume the drug spreads into (L). The "size of the tank." |
| **Elimination rate constant (k)** | CL divided by V: the fraction of caffeine removed per hour. |
| **Half-life** | Time for half of the caffeine to leave the body: 0.693 times V divided by CL. |
| **Bioavailability (F)** | Fraction of an oral dose that reaches the blood. |
| **Emax** | Maximum fraction of apneas that caffeine can remove in this infant. |
| **EC50** | Concentration that produces half of Emax. Low EC50 means a sensitive infant. |
| **Hill coefficient (h)** | Steepness of the S-shaped concentration-effect curve. |
| **Hidden state** | An unknown quantity that changes over time and must be estimated (here, clearance). |
| **Hidden parameter** | An unknown quantity that is roughly constant for one infant (here, V, Emax, EC50, maturity fade rate). |
| **Observation** | A noisy measurement used to check predictions (apnea counts, blood levels). |
| **Gray-box model** | Known equations (structure) with unknown parameters fitted from data. Between a white-box (fully known physics) and a black-box (pure data fit, such as a neural network). |
| **Inverse problem** | Given the observations and the model, find the hidden values most consistent with them. |
| **Prior** | The starting belief about a parameter before this infant's data, taken from published populations. |
| **Posterior** | The updated belief after this infant's data has been taken into account. |
| **Likelihood** | How probable the observed data is, given a set of parameter values. |
| **Poisson distribution** | The standard probability model for counting random events in a time window. |
| **Negative log-likelihood** | The loss the estimator minimizes: low when predictions match observations. |
| **Maximum a posteriori (MAP) estimate** | The single most plausible parameter values given both the data and the priors. |
| **Newton's method** | An optimization method that uses both the slope (gradient) and the curvature (Hessian) of the loss to reach its minimum in few steps. |
| **Gradient** | The vector of slopes of the loss with respect to each parameter. |
| **Hessian** | The matrix of second derivatives of the loss: its curvature. Sharp curvature means a confident estimate. |
| **Laplace approximation** | Using the inverse of the Hessian at the minimum as the uncertainty of the estimate. |
| **Automatic differentiation** | A technique that computes exact gradients and Hessians of code automatically. |
| **Identifiability** | Whether the data contain enough information to determine a parameter separately from the others. |
| **Therapeutic drug monitoring (TDM)** | Measuring the drug concentration in a blood sample. |
| **Evidence tier** | A label (A, B, C) for how strongly the literature supports a value or biomarker. |
| **Functional brain age (FBA)** | Brain maturity estimated from brain electrical activity (EEG, electroencephalography). |
| **In silico** | Performed by computer simulation. |

---

## 3. How the system works, in one page

```
            +-------------------------------------------------+
 Inputs     | covariates, dose log, monitor signals,          |
            | brain recordings, blood levels, FiO2            |
            +-----------------------+-------------------------+
                                    |
                                    v
 Features   | hourly apnea counts, valid observation time,    |
            | maturity M(t), pre-dose baseline apnea rate     |
                                    |
                                    v
 Estimator  | each hour: predict apneas -> compare with the   |
 (hourly)   | observed count -> correct the hidden values     |
            | (clearance, volume, Emax, EC50, maturity fade)  |
                                    |
                                    v
 Decision   | target concentration -> dose -> safety check    |
                                    |
                                    v
 Output     | dose suggestion + uncertainty + flags           |
            | for clinician review                            |
```

The loop is: **predict, compare, correct**, every hour. At each dosing time, the current estimate is converted into a dose suggestion.

---

## 4. Technical design

### 4.1 Time model

- **Inside the model**, time is a single number: **hours elapsed since birth**. Every dose, observation, and update lives on this one axis.
  - PNA is the time itself; PMA (in weeks) is `GA + t / (24 x 7)`. Neither is stored separately, which prevents contradictions.
- **At the boundaries** (data ingestion and display), real timestamps are timezone-aware and stored in **UTC** (Coordinated Universal Time), which avoids daylight-saving jumps. Ingestion converts them to hours since birth; display converts back to local time.
- A **clock abstraction** has two implementations:
  - a **data clock**, which follows real timestamps;
  - a **simulation clock**, which advances instantly from event to event, so days of a virtual infant run in seconds.
- Playback speed for demonstrations is a display setting of the web app only and never affects the model.

### 4.2 Variable roles

Every variable has exactly one role.

| Role | Meaning | Variables |
|---|---|---|
| **Control input** | What is given to the infant | Dose log: time, amount, route (intravenous or oral), and whether the amount is caffeine citrate or caffeine base |
| **Known covariates** | Measured facts, treated as true | GA, birth time, birth weight, weight over time, sex |
| **Exogenous context** | Known conditions not controlled by the model | FiO2, breathing support mode |
| **Measured before caffeine** | Computed from the pre-dose window | Baseline apnea rate at the time of the window |
| **Module output** | Produced by an independent module, treated as given | Maturity M(t) |
| **Observations** | Noisy measurements used to correct the model | Hourly apnea counts N, blood caffeine levels when available |
| **Computed state** | Fully determined by inputs and parameters | Caffeine amount in the body A(t) |
| **Estimated parameters (theta)** | Unknown, estimated hourly | Clearance CL (allowed to drift), volume V, Emax, EC50, maturity fade rate beta_M |
| **Fixed from registry** | Sourced values, not estimated | Hill coefficient h, reference maturity M_ref, concentration bounds, all priors and variabilities |

Caffeine citrate contains half its mass as caffeine base. Every dose and every formula states which one it uses.

### 4.3 The model chain

For each hour, the model computes the expected number of apneas from the doses and the current parameter values.

**Step 1: caffeine in the body (pharmacokinetics).** A one-compartment model treats the body as a single well-mixed tank:

```
dA/dt = -(CL / V) x A          (elimination: a constant fraction leaves per hour)
A(t)  = A(t0) x exp(-(CL / V) x (t - t0))     (between doses)
C(t)  = A(t) / V
```

- An **intravenous** dose adds `F x dose` to A instantly (F = 1).
- An **oral** dose first enters a gut compartment and moves into the blood at an absorption rate `ka`, with bioavailability F. Both values come from the registry.
- A(t) has a closed-form (exact formula) solution for both routes, so no numerical integration is needed.

**Step 2: maturity (independent module).** The maturity module combines inputs such as functional brain age, brain recording features, the SpO2/FiO2 ratio, and breathing continuity into one value per hour:

```
M(t) = maturity of the infant, in weeks
```

The estimator treats M(t) as given. How the module combines its inputs is specified separately.

**Step 3: baseline apnea rate.** Apnea of prematurity fades as the infant matures. The rate of apneas the infant would have without caffeine is:

```
lambda0(t) = lambda0_ref x exp( -beta_M x (M(t) - M_ref) )
```

- `lambda0_ref`: baseline rate at the reference maturity M_ref (derived from the pre-dose window, see 4.5).
- `beta_M`: how fast apneas fade per week of maturity (estimated).

Modeling this fade is essential: without it, improvement caused by maturation would be wrongly credited to caffeine.

**Step 4: caffeine effect (pharmacodynamics).** The Hill equation gives the S-shaped benefit curve:

```
S(C) = C^h / (EC50^h + C^h)            (fraction of the maximum effect reached)
E(C) = Emax x S(C)                     (fraction of apneas removed)
lambda(t) = lambda0(t) x (1 - E(C(t))) (apnea rate under caffeine)
```

Check: at `C = EC50`, `S = 1/2`, so the effect is half of Emax.

**Step 5: expected apneas in hour k.**

```
mu_k = integral of lambda(t) over the valid time of hour k
```

Because C changes within the hour, the integral is computed numerically over sub-steps. Only **valid time** counts (time not excluded for artifacts or disconnection, see 4.4).

### 4.4 Observations

**Apnea count N_k.** The number of qualifying apnea events whose **onset** falls inside hour k, during valid observation time.

- Event detection lives in the features layer, which reads raw signals and outputs, per hour: `N_k`, `dt_valid_k` (valid time in hours), and a data quality score. The estimator never sees raw signals.
- An event that starts in hour k and ends in hour k+1 belongs to hour k only.
- If `dt_valid_k = 0`, the hour produces no update.
- Event criteria (pause duration, heart rate and SpO2 thresholds, overlap rules) are registry entries. Bradycardia and desaturation counts are also detected and logged; whether they enter N is a registry decision.
- Each hourly record stores the version of the event definition used, so counts can be recomputed if a definition changes.

**Blood caffeine level.** A laboratory measurement of concentration from a small blood sample, at a recorded time. It is the closest thing to ground truth, with a known assay error. It is the only observation that sees concentration directly, which makes it the strongest anchor for CL and V.

### 4.5 The estimator

The estimator solves an **inverse problem**: find the parameter values most consistent with the observations. It runs **recursively**: every hour, it uses only the new hour's data plus a memory of everything before.

**Estimated parameters (theta).** Each is transformed so the optimizer can move freely without breaking physical limits:

```
theta = ( log CL , log V , logit Emax , log EC50 , log beta_M )
```

- `log` keeps CL, V, EC50, and beta_M positive.
- `logit(Emax) = log(Emax / (1 - Emax))` keeps Emax between 0 and 1.

**Baseline apnea rate.** Computed in the features layer from the pre-dose window: total qualifying events divided by total valid hours. It is a fixed input, not part of theta. Its conversion to the reference maturity, `lambda0_ref = lambda0_measured / exp(-beta_M x (M_window - M_ref))`, happens inside the model chain, since beta_M is estimated. Its Poisson standard error (square root of the count, divided by valid hours) is stored for reporting. If no pre-dose window exists, a population fallback from the registry is used and every output carries the flag `no_baseline_window`.

**The loss at hour k.**

```
Loss_k(theta) =
    [ mu_k - N_k x log(mu_k) ]                                         apnea term
  + [ (log C_measured - log C_predicted)^2 / (2 x sigma_assay^2) ]     blood term (when available)
  + 1/2 x (theta - theta_prev)^T x Sigma_prior^-1 x (theta - theta_prev)  memory term
  + barrier(C)                                                         bounds term
```

- **Apnea term:** the negative log of the Poisson likelihood (constant terms dropped). It is small when the predicted count matches the observed one.
- **Blood term:** the error between measured and predicted concentration in log space, since laboratory error scales with the value.
- **Memory term:** summarizes all earlier hours as a penalty around last hour's estimate. Yesterday's posterior becomes today's prior. This is equivalent to regularization (weight decay) in neural network training.
- **Bounds term:** a barrier that grows steeply as the predicted concentration approaches the sourced bounds.

**Clearance drift.** Clearance rises as the infant matures. Before each hour, the memory is loosened in the clearance direction only:

```
Sigma_prior = Sigma_prev + Q
Q = diag( sigma_drift^2 , 0 , 0 , 0 , 0 )
```

**Minimization.** Newton's method, starting from last hour's estimate. Gradients and Hessians are computed by automatic differentiation. The chain rule links every parameter to the loss through mu_k; for example, `d(apnea term)/d(mu_k) = 1 - N_k / mu_k`, so if more apneas were observed than predicted, the update moves toward parameters that predict more apneas.

**Uncertainty.** At the minimum, the Hessian H_k gives the new uncertainty (Laplace approximation):

```
Sigma_k = H_k^-1
```

**Initialization (hour 0).**

```
theta_0 = ( log CL_typical , log V_typical , logit Emax_pop , log EC50_pop , log beta_M_pop )
Sigma_0 = diag( omega_CL^2 , omega_V^2 , omega_Emax^2 , omega_EC50^2 , omega_beta^2 )
```

`CL_typical` and `V_typical` come from the population pharmacokinetic model selected in the run configuration, evaluated at the infant's covariates. The `omega` values (inter-individual variability) come from the registry.

**The hourly loop.**

1. Loosen the memory for clearance drift.
2. Build Loss_k from the new apnea count, any blood level, the memory, and the bounds.
3. Minimize from the previous estimate with Newton's method.
4. Compute the Hessian and the new uncertainty.
5. Store the estimate and its uncertainty; at dosing time, run the decision.

### 4.6 What can and cannot be learned

From apnea counts alone, the estimator sees only the product of baseline rate and caffeine effect. Different combinations of parameters can produce the same count. Each parameter becomes learnable only when the data contain a situation that isolates it:

| Parameter | Learnable from | Notes |
|---|---|---|
| Baseline apnea rate | Pre-dose window | Measured directly when caffeine is absent |
| CL, V | Blood levels | Apnea counts reach them only indirectly; V stays near its prior without blood levels |
| Emax, EC50 | Apnea counts at several distinct concentrations | Needs concentrations spread along the curve; slow decay in preterm infants clusters them |
| beta_M | Weeks of data, plus blood levels | Confounded early with caffeine accumulation, which also reduces apneas |

Parameters that the data cannot separate do not break the system: they stay near their prior, and their uncertainty stays wide. Virtual-infant runs measure which parameters converge in practice (see 4.10).

### 4.7 The dose decision

**Target concentration.** The lowest concentration reaching a chosen fraction f of this infant's maximum effect, found by inverting the Hill equation:

```
C_f = EC50 x ( f / (1 - f) )^(1/h)
C_target = max( C_min , min( C_f , C_max ) )
```

- `f`, `C_min`, `C_max`: from the registry.
- Aiming for a fraction instead of the maximum avoids diminishing returns: as f approaches 1, the required concentration grows without limit while the extra benefit approaches zero.

**From target to dose.** With the estimated CL and V:

```
maintenance dose   D      = C_target x CL x tau / F     (tau = dosing interval)
loading dose       D_load = C_target x V / F
```

Clearance sets the maintenance dose; volume sets the loading dose. The caffeine already in the body, A(t), is accounted for by simulating each candidate dose forward from the current state.

**Safety check.** Parameter samples are drawn from the current estimate and its uncertainty. Each sample is simulated forward with the candidate dose. The share of samples whose concentration exceeds C_max must stay below epsilon (from the registry); otherwise the dose is lowered.

**Confidence gate.** While uncertainty is wide, the suggestion stays at the standard regimen. It may deviate only as the uncertainty narrows.

**Output.** The suggested dose, the predicted concentration range, the current parameter estimates with their uncertainty, and flags (high heart rate, wide uncertainty, excluded hours, no baseline window). Always for clinician review.

**Toxicity in this version** is handled entirely by the sourced concentration bounds. Heart rate is used as a safety flag only.

### 4.8 Parameter registry

Every physiological value, formula, and threshold lives in the registry, never in code.

- Stored as data files, one per category (pharmacokinetic models, effect, maturity, priors, bounds, events, validation ranges, decision), read by a loader and validator.
- Every entry has: name, value, unit, plain-language meaning, evidence tier, population of validity (structured ranges of GA, PNA, weight), and one or more structured citations including the exact table or equation.
- Formula entries also list the equation and define every symbol.
- Several published population pharmacokinetic models are stored side by side and selected by name in the run configuration. Conflicts between sources are labeled, never silently resolved.
- Units are checked by a units library.
- The registry carries a version number and a changelog; every run records the version it used.
- **A run refuses to start if any entry it requires is empty**, and lists all missing entries at once.

**Evidence tiers.**

| Tier | Meaning |
|---|---|
| **A** | Replicated across several independent studies |
| **B** | One solid study, or several small consistent studies |
| **C** | A single exploratory study, a preprint, or evidence from a related but different context |

### 4.9 Run configuration

Numerical and procedural settings that are not physiological live in the run configuration, separate from the registry: selected pharmacokinetic model, mode, random seed, Newton's method settings (tolerance, iteration limit, safeguards), barrier form and strength, number of safety samples, and dose rounding.

### 4.10 Modes and validation

**Virtual-infant mode.** A simulator generates infants with **known true parameters**, simulates their concentrations under a dosing schedule, and produces apnea counts, blood levels with assay error, artifacts, and missing periods. The estimator runs blind, starting from the population prior. Metrics:

- **Convergence:** time until each parameter's estimate approaches its true value.
- **Coverage:** whether the stated uncertainty intervals contain the true value as often as they claim. Lower coverage means the estimator is overconfident.
- **Identifiability table:** which parameters converge and which stay at their prior.
- **Dose quality:** suggested dose versus the dose that would be optimal given the true parameters.

**Real-data mode.** Planned in phases, so that learning never depends on an untested suggestion being given to an infant. The estimator learns from whatever dose was actually given, whoever chose it:

1. **Retrospective:** run on past records containing doses and apnea counts.
2. **Shadow:** run live alongside clinicians, who dose as usual; suggestions are logged for comparison only.
3. **Advisory:** suggestions shown to clinicians for approval.

Doses are never varied on purpose to help the model learn.

---

## 5. Repository structure

```
NeoCaffeine-preterms-caffeine-dose/
  README.md
  pyproject.toml
  .gitignore
  config/                 run configuration
  docs/
    DECISIONS.md          dated log of every design decision
    proposals/            design proposals awaiting approval
  neocaffeine/            the Python package
    patient/              patient object, dose log, observation logs
    registry/             registry data files, loader, validator
    ingest/               loading real patient records
    features/             event detection, valid time, pre-dose baseline
    maturity/             independent maturity module
    models/               pharmacokinetics, baseline, effect, expected apneas
    estimator/            loss terms, Newton steps, recursive update
    decision/             target concentration, dose, safety check
    simulator/            virtual infants
    runner/               the hourly loop for both modes
    evaluation/           convergence, coverage, dose quality
  tests/                  mirrors the package
  webapp/                 user interface (to be developed)
```

Each folder contains its own README describing its role and connections. Code files carry a short header describing their purpose and no other comments.

---

## 6. Data policy

- **No patient data is ever committed** to this repository, real or exported. Any local data folder is excluded by `.gitignore`.
- Virtual-infant outputs may be committed.

---

## 7. Limitations

- **Simulation first.** The system has not yet been validated on real infants.
- **Identifiability.** With apnea counts alone, several parameters remain close to their priors; blood levels and a pre-dose window are needed to separate them.
- **Maturity module.** Its inputs (functional brain age, the SpO2/FiO2 ratio) are candidate biomarkers, not validated predictors of caffeine response. Caffeine itself may alter brain recording features, creating a possible feedback between the drug and the maturity signal.
- **Event model.** Apneas tend to cluster, which can make counts more variable than the Poisson model assumes.
- **Toxicity** is handled by population concentration bounds, not by an infant-specific model.
- **Confounders.** Infection, anemia, other drugs, and changes in respiratory support affect apneas and are only partly represented.
- **Clinical data** on caffeine dosing are scarce, and most apneas are missing from clinical notes.

---

## 8. Roadmap

- Toxicity as an estimated, infant-specific property.
- Negative binomial likelihood if apnea counts prove overdispersed.
- Hierarchical estimation: pooling estimates such as beta_M across infants to learn better priors.
- Hybrid models: a small neural network inside the equations, learning only what the physiology misses.
- Federated calibration across hospitals, sharing parameter distributions instead of raw data.
- The web app.

---

## 9. References

1. Eichenwald EC, Committee on Fetus and Newborn. Apnea of prematurity. *Pediatrics.* 2016.
2. Robertson CM, et al. Outcomes of infants with apnea of prematurity. 2009.
3. Schmidt B, et al. Caffeine therapy for apnea of prematurity. *New England Journal of Medicine.* 2006.
4. Schmidt B, et al. Long-term effects of caffeine therapy for apnea of prematurity. *New England Journal of Medicine.* 2007.
5. World Health Organization. Recommendations for care of the preterm or low-birth-weight infant. 2022.
6. Natarajan G, et al. Therapeutic drug monitoring for caffeine in preterm neonates. 2007.
7. Sugino M, et al. Serum caffeine concentrations in preterm infants. 2023.
8. Engbers AGJ, et al. Pharmacokinetics of caffeine in preterm infants. 2021.
9. Koch G, et al. Caffeine citrate dosing adjustments in preterm infants. 2017.
10. Bhatti AI. On estimating phenomenological model states for epileptic seizure prediction. *Frontiers in Applied Mathematics and Statistics.* 2026;12:1709607. doi:10.3389/fams.2026.1709607
11. Kovatchev BP, et al. In silico preclinical trials: a proof of concept in closed-loop control of type 1 diabetes. *Journal of Diabetes Science and Technology.* 2009.
12. Li L, et al. Optimal channel and feature selection for automatic prediction of functional brain age of preterm infant based on EEG. *Frontiers in Neuroscience.* 2025;19:1517141. doi:10.3389/fnins.2025.1517141

Population pharmacokinetic models stored in the registry (Thomson 1996, Falcao 1997, Charles 2008, Gao 2020, Engbers 2021) are cited in full in their registry entries.