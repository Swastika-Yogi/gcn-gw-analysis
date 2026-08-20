---
project_name: "GW Pathfinder / Pre-Catalog Chirp Mass Estimation"
project_type: "Bachelor's thesis project with longer-term research-paper extension"
domain: "Gravitational-wave astronomy / GCN Circulars / scientific data processing"
primary_language: "Python"
document_purpose: "Context file for a coding assistant (Claude) to understand the project, intended pipeline, mathematical model, assumptions, and near-term implementation goals."
status: "Active / being restarted after a pause"
priority: "Finish a coherent bachelor's-level project first; continue deeper research afterward"
---

# 1. Executive Summary

This project started as **GW Pathfinder**, a chatbot-style interface for gravitational-wave (GW) data.

The research direction later expanded toward a more scientific problem:

> Can we use information available in early **GCN Circulars** to obtain a fast, approximate estimate of the **chirp mass** of a gravitational-wave event before full parameter-estimation/catalog values are available?

The current intended workflow is:

```text
GCN Circulars
    -> identify GW-related circulars
    -> group circulars by event
    -> extract useful parameters
    -> build a structured event-level dataset
    -> apply a simplified chirp-mass estimation model
    -> compare estimates with later/published reference values
    -> quantify error, bias, and limitations
```

For the **bachelor's thesis**, the project does not need to solve the full research problem perfectly. A complete, defensible pipeline with honest evaluation is enough.

The longer-term **paper** may continue improving the estimator and testing it on future events.

---

# 2. Core Research Question

Primary research question:

> Can chirp mass be approximately estimated from GCN Circular-level information using simplified gravitational-wave scaling relations and controlled approximations?

Secondary engineering question:

> Can raw GCN Circular text be automatically converted into a structured dataset containing the observables needed for this estimation?

---

# 3. Important Scope Clarification

There are two related but distinct project layers.

## 3.1 Thesis / near-term implementation

Preferred scope:

1. Collect or load GCN Circulars.
2. Identify GW events.
3. Group multiple Circulars belonging to the same event.
4. Extract useful parameters.
5. Build a clean event-level table.
6. Implement a first chirp-mass estimator.
7. Compare against reference/published values where possible.
8. Report performance and limitations.

## 3.2 Longer-term research / paper

Potential later work:

- improve physical calibration;
- use better detector-noise information;
- improve treatment of orientation;
- propagate uncertainties rigorously;
- separate models by observing run or detector network;
- test predictions on genuinely new events before later values are released;
- possibly integrate the estimator into the GW Pathfinder chatbot.

## 3.3 What is NOT required right now

Do not make these blockers for the bachelor's thesis:

- full Bayesian parameter estimation;
- full waveform inference;
- production-grade chatbot;
- live alert service;
- sophisticated machine learning;
- exact detector characterization for every event;
- publication-level final physics model.

---

# 4. Scientific Quantity of Interest

The target parameter is the **chirp mass**.

For component masses \(m_1\) and \(m_2\):

\[
\mathcal{M} =
\frac{(m_1 m_2)^{3/5}}
{(m_1 + m_2)^{1/5}}
\]

The project is attempting to estimate \(\mathcal{M}\) indirectly from early observational information.

---

# 5. Mathematical Model Currently Being Explored

The uploaded methodology note starts from a standard inspiral SNR scaling and rewrites it into a simplified chirp-mass estimator.

The note uses the approximate dependence:

\[
\rho^2 \propto
\frac{\mathcal{M}_z^{5/3}}{D_L^2}
\left[
F_+^2(1+\cos^2\iota)^2
+
4F_\times^2\cos^2\iota
\right]
I_7
\]

where:

- \(\rho\) = signal-to-noise ratio (SNR)
- \(D_L\) = luminosity distance
- \(\iota\) = inclination angle
- \(F_+\), \(F_\times\) = detector antenna-pattern factors
- \(I_7\) = detector noise integral
- \(\mathcal{M}_z\) = redshifted chirp mass

The note defines a combined orientation factor:

\[
F(\iota)
=
\left[
F_+^2(1+\cos^2\iota)^2
+
4F_\times^2\cos^2\iota
\right]^{1/2}
\]

which gives the scaling:

\[
\rho
\propto
\frac{\mathcal{M}_z^{5/6}}{D_L}
F(\iota) I_7^{1/2}
\]

Rearranging:

\[
\mathcal{M}_z
\propto
\left(
\frac{\rho D_L}
{F(\iota) I_7^{1/2}}
\right)^{6/5}
\]

The note then absorbs detector/noise/unit terms into a calibration constant \(C\), producing a working form conceptually like:

\[
\hat{\mathcal{M}}_z
=
C
\left(
\frac{\rho D_L}{F(\iota)}
\right)^{6/5}
\]

IMPORTANT:

- This is a **working approximation**, not yet a validated final estimator.
- Do not treat \(C\), SNR assumptions, or orientation assumptions as scientifically settled.
- Part of the project is to determine whether this approximation is useful at all.

---

# 6. Detector Noise Term

The methodology note defines:

\[
I_7 = \int \frac{f^{-7/3}}{S_n(f)} \, df
\]

It depends on:

- detector sensitivity;
- detector noise power spectral density \(S_n(f)\);
- frequency range.

The note proposes absorbing \(I_7^{1/2}\) into an effective constant \(C\) because this information is generally not directly available in GCN Circulars.

This is a simplification that must be treated as an assumption/calibration choice, not as an exact physical removal of detector dependence.

---

# 7. Information Expected from GCN Circulars

Useful event-level fields may include:

```yaml
event_fields:
  event_id:
    examples: ["S230518h"]
    importance: "required for grouping and cross-matching"

  event_time:
    importance: "event identification / ordering"

  luminosity_distance:
    symbol: "D_L"
    units: "Mpc or Gpc"
    importance: "core estimator input"

  luminosity_distance_uncertainty:
    importance: "uncertainty analysis"

  classification:
    examples: ["BBH", "BNS", "NSBH"]
    importance: "source-type context / possible prior information"

  classification_probabilities:
    importance: "confidence / source-type interpretation"

  far:
    full_name: "False Alarm Rate"
    importance: "detection significance; NOT automatically equivalent to SNR"

  snr:
    symbol: "rho"
    availability: "may be absent"
    importance: "core estimator input if genuinely available"

  sky_localization:
    importance: "context; not necessarily required by the first estimator"

  circular_id:
    importance: "traceability"

  circular_text:
    importance: "raw source text for audit/debugging"
```

---

# 8. Information Often Missing or Not Directly Available

Potentially missing quantities include:

```yaml
missing_or_approximated:
  inclination:
    symbol: "iota"
    proposed_treatment: "representative/average orientation or marginalization"

  antenna_pattern:
    symbols: ["F_+", "F_x"]
    proposed_treatment: "effective orientation factor or calibration"

  detector_noise_integral:
    symbol: "I_7"
    proposed_treatment: "absorb into calibration constant or later model detector/run dependence"

  exact_snr:
    symbol: "rho"
    warning: "Do not infer SNR directly from FAR without a defensible mapping."

  waveform_details:
    proposed_treatment: "ignored in first-order model"

  spin_effects:
    proposed_treatment: "ignored in first-order model"

  polarization:
    proposed_treatment: "absorbed into effective orientation treatment"

  redshift:
    proposed_treatment: "derive only if needed and if cosmology assumptions are explicit"
```

---

# 9. Critical Scientific Warnings for Coding

Claude should NOT silently implement unsupported assumptions.

## 9.1 FAR is not SNR

A low FAR indicates a significant detection, but FAR is not numerically interchangeable with SNR.

If exact/network SNR is unavailable:

- mark SNR as missing;
- keep any assumed SNR explicitly configurable;
- distinguish measured vs assumed values;
- run sensitivity tests across plausible SNR values rather than hard-coding one value.

## 9.2 Orientation should be explicit

If using a representative orientation:

- keep it as a named model assumption;
- make it configurable;
- ideally test multiple orientations or an orientation distribution.

## 9.3 Calibration constant C must be learned or justified

Do not use an arbitrary constant as though it is a physical universal.

Possible strategy:

1. select training/calibration events with known reference chirp masses;
2. fit \(C\) on calibration events;
3. evaluate on held-out events;
4. report error.

Avoid calibrating and evaluating on the exact same events without clearly labeling that result as in-sample.

## 9.4 Source-frame vs detector-frame chirp mass

Be explicit about whether the model estimates:

- detector-frame/redshifted chirp mass \(\mathcal{M}_z\), or
- source-frame chirp mass \(\mathcal{M}\).

Do not mix them in validation.

---

# 10. Intended Data Pipeline

Suggested modular architecture:

```text
src/
  ingestion/
    load_gcn_archive.py
    fetch_or_read_circulars.py

  parsing/
    event_id_parser.py
    distance_parser.py
    far_parser.py
    classification_parser.py
    snr_parser.py

  processing/
    group_by_event.py
    normalize_units.py
    resolve_duplicate_values.py
    build_event_table.py

  modeling/
    chirp_mass_estimator.py
    calibration.py
    uncertainty.py

  validation/
    load_reference_catalog.py
    match_events.py
    metrics.py

  analysis/
    plots.py
    reports.py

data/
  raw/
  interim/
  processed/

notebooks/
tests/
```

This architecture is a recommendation, not proof that the current repository already uses these filenames.

---

# 11. Expected Event-Level Dataset

Preferred output schema:

```yaml
columns:
  - event_id
  - event_time
  - circular_ids
  - luminosity_distance_mpc
  - luminosity_distance_lower_mpc
  - luminosity_distance_upper_mpc
  - far_value
  - far_unit
  - snr
  - snr_source        # measured / extracted / assumed / missing
  - p_bbh
  - p_bns
  - p_nsbh
  - p_terrestrial
  - source_class
  - raw_text_count
  - extraction_notes
  - data_quality_flags
  - reference_chirp_mass
  - reference_mass_frame
  - estimated_chirp_mass
  - absolute_error
  - percentage_error
```

Do not force every field to be present.

Missingness is scientifically meaningful.

---

# 12. Parsing Requirements

The parser should:

1. preserve the raw Circular text;
2. identify event IDs robustly;
3. support multiple Circulars per event;
4. normalize distance units;
5. preserve uncertainty ranges;
6. record provenance for every extracted value;
7. avoid silently replacing conflicting values;
8. prefer later/revised Circular values only if the rule is explicit;
9. log parsing failures;
10. make regex patterns testable.

Example provenance object:

```json
{
  "event_id": "SXXXXXXx",
  "field": "luminosity_distance_mpc",
  "value": 1200.0,
  "source_circular_id": 12345,
  "source_text": "The luminosity distance is ...",
  "parser": "distance_regex_v2",
  "confidence": "high"
}
```

---

# 13. Model Interface

Suggested estimator interface:

```python
estimate_chirp_mass(
    distance_mpc,
    snr,
    orientation_factor,
    calibration_constant,
    mass_frame="detector"
)
```

Do not bury assumptions inside the function.

All assumptions should be passed explicitly or stored in a configuration object.

Example configuration:

```yaml
model:
  version: "baseline_v1"
  orientation_strategy: "fixed"
  orientation_factor: null
  snr_strategy: "extracted_only"
  calibration_strategy: "fit_on_training_events"
  mass_frame: "detector"
```

---

# 14. Validation Strategy

Minimum useful evaluation:

```yaml
metrics:
  - mean_absolute_error
  - root_mean_squared_error
  - median_absolute_percentage_error
  - bias
  - number_of_events
```

Recommended experiments:

### Experiment A: Data availability

Question:
> For how many GW events do Circulars contain the fields required by the baseline estimator?

Output:
- count/percentage with distance;
- count/percentage with SNR;
- count/percentage with classification;
- complete-case count.

### Experiment B: Baseline estimator

Use only events with sufficiently complete inputs.

Compare estimated vs reference chirp mass.

### Experiment C: Sensitivity to SNR assumption

If SNR is missing, evaluate results over a range instead of using one hidden fixed number.

### Experiment D: Sensitivity to orientation

Test representative orientation choices or samples from an isotropic orientation model.

### Experiment E: Calibration generalization

Fit \(C\) on one subset, evaluate on another.

---

# 15. Interpretation of Results

A successful project does NOT require extremely accurate predictions.

Scientifically valid outcomes include:

```yaml
possible_outcomes:
  strong_result:
    description: "Estimator achieves useful accuracy across a meaningful subset of events."

  conditional_result:
    description: "Estimator is useful only for specific event classes or data-quality conditions."

  weak_result:
    description: "Circular-level information is insufficient for reliable chirp-mass estimation under the current model."

  engineering_result:
    description: "The main successful contribution is a reproducible GCN-to-structured-GW-event data pipeline."
```

A negative result is still informative if the limitations are demonstrated rigorously.

---

# 16. Relationship to GW Pathfinder Chatbot

Original concept:

```text
User
  -> GW Pathfinder chatbot
  -> query/explain GW events
```

Possible future architecture:

```text
User
  -> GW Pathfinder
  -> structured GW data layer
      -> official catalogs
      -> GCN Circular parser
      -> early-estimation module
  -> answer/explanation
```

Therefore:

- the chatbot is an application layer;
- the GCN parser is a data layer;
- the chirp-mass estimator is a scientific inference layer.

They do not have to be completed simultaneously.

---

# 17. Immediate Coding Priorities

Claude should help in this order unless the repository shows a better state:

```yaml
priority_tasks:
  1: "Inspect existing repository and summarize what already works."
  2: "Identify the actual entry points/scripts and data flow."
  3: "Run current code before rewriting anything."
  4: "List broken/incomplete components."
  5: "Verify GCN parsing against real examples."
  6: "Create a clean event-level dataframe."
  7: "Add provenance and missing-value handling."
  8: "Implement baseline chirp-mass estimator as a separate module."
  9: "Create calibration/validation split."
  10: "Produce reproducible evaluation output."
```

---

# 18. Instructions to Claude When Reading the Repository

When this file is provided alongside the codebase:

1. **Inspect before refactoring.**
2. Explain the current repository structure.
3. Identify what code corresponds to:
   - ingestion,
   - GCN filtering,
   - event grouping,
   - parameter extraction,
   - estimation,
   - validation.
4. State which parts are implemented, partial, duplicated, or missing.
5. Do not invent missing files/functions.
6. Preserve working code where possible.
7. Suggest the smallest changes needed for a complete bachelor's-level project.
8. Keep research assumptions separate from software assumptions.
9. Ask before making major architectural rewrites.
10. Prefer reproducibility and traceability over cleverness.

---

# 19. Near-Term Definition of Done

For the bachelor's project, "done" can mean:

```yaml
definition_of_done:
  - "Raw/archived GCN Circulars can be processed reproducibly."
  - "GW events can be identified and grouped."
  - "A structured event dataset is generated."
  - "Useful parameters and missingness are documented."
  - "A baseline chirp-mass estimation method is implemented."
  - "The method is tested on historical/reference events."
  - "Errors and limitations are reported honestly."
  - "The pipeline can be demonstrated end-to-end."
```

A chatbot is optional for this milestone.

---

# 20. Open Questions

These should remain explicit until confirmed:

```yaml
open_questions:
  - "Is the bachelor's thesis centered on the GCN pipeline, the estimator, or GW Pathfinder?"
  - "What exact observing-run interval should be used?"
  - "What reference catalog/value set should be used for validation?"
  - "Is usable SNR actually present in enough Circulars?"
  - "Should the estimator target detector-frame or source-frame chirp mass?"
  - "How should orientation be treated?"
  - "Should C be global, run-specific, detector-network-specific, or event-class-specific?"
  - "Can FAR contribute to the model, or should it remain a significance/quality field only?"
  - "How many historical events are sufficiently complete for validation?"
```

---

# 21. Coding Assistant Goal

The coding assistant's job is NOT merely to generate code.

The goal is to help transform the current repository into a **small, reproducible scientific pipeline** whose assumptions and outputs are understandable enough to be defended in a bachelor's thesis and extended later into a research paper.

When uncertain about physics, mark the uncertainty rather than silently encoding an assumption.
