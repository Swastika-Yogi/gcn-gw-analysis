# GW Thesis Master Project Plan

> **Document type:** Living project plan / machine-readable Markdown
> **Version:** 0.1
> **Status:** Provisional — revise when code, literature, or data changes the direction
> **Core principle:** GW-Pathfinder, the GCN Circular pipeline, and chirp-mass investigation are components of one evolving project, not separate competing projects.

---

## 0. Project Definition

### Working project story

`AI/computational tools in GW astronomy -> GW-Pathfinder -> GW data access and processing -> GCN Circular extraction -> structured early-event data -> scientific analysis -> approximate chirp-mass estimation case study -> validation against catalogued events -> integrated GW research-support framework`

### Current working objective

Develop and evaluate a gravitational-wave information framework that combines structured GW data access, automated processing of GCN Circulars, and scientifically useful analysis, with approximate pre-catalog chirp-mass estimation investigated as a case study and GW-Pathfinder providing the broader intelligent-access/interface concept.

### Rules for this plan

- [ ] Do not treat the chatbot and chirp-mass work as separate thesis projects.
- [ ] Do not claim successful chirp-mass estimation until calculations are reproduced and validated.
- [ ] Do not rebuild existing code until old code has been located, understood, and tested.
- [ ] Write thesis material in parallel with technical work.
- [ ] Preserve room for new literature, new parameters, new datasets, and revised scientific questions.
- [ ] Separate established physics, implemented work, experimental assumptions, and future work.
- [ ] Prefer a smaller reproducible result over an impressive but unsupported claim.

---

# MILESTONE 1 — Recover, Audit, and Define the Existing Project

**Goal:** Establish exactly what already exists and create a reliable starting point.

**Status:** `TODO`

## M1.1 — Project inventory

- [ ] Locate original GW-Pathfinder proposal.
- [ ] Locate chirp-mass working notes.
- [ ] Locate all existing Python scripts/notebooks.
- [ ] Locate downloaded GCN datasets.
- [ ] Locate cleaned/intermediate datasets.
- [ ] Locate GWTC/catalog datasets previously used.
- [ ] Locate chatbot/vector database/embedding experiments, if any.
- [ ] Locate figures, tables, calculations, and presentation material.
- [ ] Locate previous literature/papers.
- [ ] Record GitHub repositories and branches, if they exist.
- [ ] Record local/cloud locations of all project assets.

### Deliverable

`project_inventory.md`

Suggested fields per item:

```yaml
name:
type: code|dataset|paper|note|figure|model|other
location:
purpose:
status: working|partial|unknown|obsolete
last_known_result:
dependencies:
needs_review: true|false
```

## M1.2 — Code audit

- [ ] Open every important script/notebook.
- [ ] Record what each file is intended to do.
- [ ] Identify required Python packages.
- [ ] Identify external APIs/web sources.
- [ ] Identify hard-coded paths and credentials.
- [ ] Determine expected inputs and outputs.
- [ ] Run code without modifying scientific logic first.
- [ ] Record errors.
- [ ] Mark code as `WORKING`, `BROKEN`, `UNKNOWN`, or `OBSOLETE`.
- [ ] Avoid rewriting working components unnecessarily.

### Deliverable

`code_audit.md`

## M1.3 — Thesis skeleton v0.1

Create provisional chapters:

- [ ] Abstract placeholder
- [ ] Introduction
- [ ] Research background / literature review
- [ ] Gravitational-wave data ecosystem
- [ ] GW-Pathfinder concept and architecture
- [ ] GCN Circular acquisition and processing
- [ ] Dataset construction
- [ ] Scientific inference / chirp-mass case study
- [ ] Implementation
- [ ] Experiments and validation
- [ ] Results
- [ ] Discussion and limitations
- [ ] Conclusion
- [ ] Future work
- [ ] References
- [ ] Appendices

### Exit criteria for Milestone 1

- Existing work is mapped.
- Important code has been attempted at least once.
- No major previous component is being accidentally discarded.
- Thesis structure exists but remains editable.

---

# MILESTONE 2 — Literature and Comparative Research

**Goal:** Establish the scientific and computational context and identify the gap the thesis addresses.

**Status:** `TODO`

## M2.1 — Literature groups

Collect and annotate literature under these groups:

### A. GW fundamentals

- [ ] Compact binary coalescence
- [ ] Chirp mass
- [ ] SNR and detector sensitivity
- [ ] Luminosity distance
- [ ] Source classification
- [ ] Parameter estimation
- [ ] Low-latency GW analysis

### B. GW data infrastructure

- [ ] GWOSC
- [ ] GWTC catalogs
- [ ] GraceDB / public alerts where relevant
- [ ] GCN Notices
- [ ] GCN Circulars
- [ ] O1/O2/O3/O4 observing-run differences relevant to this project

### C. AI/computational methods in GW astronomy

- [ ] Machine learning for detection
- [ ] ML for parameter estimation
- [ ] Deep learning for waveform/data analysis
- [ ] NLP/information extraction in astronomy
- [ ] LLM/agent/retrieval systems for scientific data
- [ ] Semantic search/vector databases in scientific applications
- [ ] Automated astronomical alert processing

### D. Related inspiration

- [ ] Paper(s) using circulars/notices for GRB or other transient inference
- [ ] Identify exactly which idea was adapted from each paper.
- [ ] Distinguish inspiration from direct methodological adoption.

### E. Chirp-mass/SNR relation

- [ ] Verify source for starting SNR relation.
- [ ] Verify chirp-mass dependence.
- [ ] Verify detector noise integral treatment.
- [ ] Verify redshifted vs source-frame chirp mass.
- [ ] Identify what is literature-derived versus introduced by this project.

## M2.2 — Literature database

For every important paper record:

```yaml
paper_id:
title:
authors:
year:
doi_or_url:
category:
problem:
data_used:
method:
main_result:
relevance_to_thesis:
idea_used_by_us:
limitations:
where_to_cite_in_thesis:
```

## M2.3 — Comparative analysis

Create a comparison table of existing approaches.

Candidate columns:

- Tool/paper
- GW task
- Data source
- AI/ML/NLP method
- Real-time or retrospective
- User-facing interface
- Automated extraction
- Parameter inference
- Strength
- Limitation
- Relation to GW-Pathfinder

### Thesis outputs

- [ ] Literature comparison table
- [ ] Timeline/diagram of computational approaches in GW research
- [ ] Research-gap paragraph
- [ ] Background chapter draft

### Exit criteria

We can clearly answer:

1. What has already been done?
2. What problem remains?
3. Why combine intelligent access with automated GW alert processing?
4. What part of our work is implementation?
5. What part is scientific experimentation?

---

# MILESTONE 3 — Build the GW Data Foundation

**Goal:** Create reproducible structured data from reliable GW sources.

**Status:** `TODO`

## M3.1 — Catalog/reference dataset

- [ ] Identify appropriate published GW catalogs.
- [ ] Download/reference event metadata.
- [ ] Standardize event identifiers.
- [ ] Extract relevant reference parameters.
- [ ] Preserve uncertainty intervals where available.
- [ ] Record source/catalog version.

Potential fields:

```text
event_id
gps_time
observing_run
source_class
chirp_mass_source
chirp_mass_detector
component_mass_1
component_mass_2
luminosity_distance
redshift
network_snr
far
spin_parameters
reference_source
```

## M3.2 — Historical validation dataset

- [ ] Select events from previous runs with known catalog values.
- [ ] Determine whether corresponding early-alert/Circular information exists.
- [ ] Build a mapping between early information and final catalog values.
- [ ] Prevent leakage of final catalog values into estimator inputs.

### Important experimental principle

Historical events should simulate the question:

> "What could we have inferred using only information available at the early-alert/Circular stage?"

## M3.3 — Current/O4 dataset

- [ ] Recover previous O4/O4a extraction.
- [ ] Verify reported ~44,000 Circular parsing step.
- [ ] Verify keyword filtering logic.
- [ ] Verify reported ~150 candidate events.
- [ ] Verify reported ~70 usable events.
- [ ] Recalculate counts rather than trusting notes.
- [ ] Extend beyond O4a if scientifically useful and feasible.

### Exit criteria

- Reference catalog dataset exists.
- Historical validation subset exists.
- Current/O4 Circular dataset exists.
- Event IDs can be cross-matched reliably.

---

# MILESTONE 4 — GCN Circular Processing Pipeline

**Goal:** Convert unstructured Circular text into reproducible structured GW-event information.

**Status:** `TODO`

## M4.1 — Acquisition

- [ ] Define source and retrieval mechanism.
- [ ] Save raw Circular metadata.
- [ ] Save raw text where permitted/appropriate.
- [ ] Record Circular ID, date, author, subject, event association.
- [ ] Make acquisition reproducible.

## M4.2 — GW Circular identification

- [ ] Develop keyword/rule-based baseline.
- [ ] Test event-name recognition.
- [ ] Test compact-binary candidate identification.
- [ ] Remove irrelevant Circulars.
- [ ] Handle multiple Circulars associated with one event.
- [ ] Measure false positives/false negatives on a manually checked sample.

## M4.3 — Parameter extraction

Attempt extraction of all useful fields, not only chirp-mass inputs.

Candidate fields:

```yaml
event_id:
circular_id:
event_time:
alert_type:
source_classification:
classification_probabilities:
far:
luminosity_distance:
luminosity_distance_uncertainty:
snr:
sky_area:
ra:
dec:
has_ns:
has_remnant:
terrestrial_probability:
detectors:
other_reported_parameters:
source_text_span:
```

- [ ] Define regex/rule extraction baseline.
- [ ] Consider NLP/LLM-assisted extraction only where useful.
- [ ] Preserve original text span for provenance.
- [ ] Represent missing values explicitly.
- [ ] Normalize units.
- [ ] Normalize probability formats.
- [ ] Record extraction confidence where possible.

## M4.4 — Extraction evaluation

Create a manually annotated gold sample.

- [ ] Randomly select representative Circulars.
- [ ] Manually record true values.
- [ ] Compare automated extraction.
- [ ] Calculate field-level precision.
- [ ] Calculate recall.
- [ ] Calculate F1 where meaningful.
- [ ] Calculate numerical extraction error where meaningful.
- [ ] Analyze failure cases.

### Figures/tables

- [ ] Pipeline architecture diagram
- [ ] Number of Circulars at each filtering stage
- [ ] Parameter availability bar chart
- [ ] Missing-data heatmap
- [ ] Extraction accuracy table
- [ ] Example raw Circular → structured record figure

### Exit criteria

A new Circular can pass through the pipeline and produce a structured, traceable event record.

---

# MILESTONE 5 — Circular Information Availability Study

**Goal:** Quantify what information Circulars actually provide before deciding what inference is defensible.

**Status:** `TODO`

## M5.1 — Availability analysis

For each parameter calculate:

- [ ] Number of events containing it
- [ ] Percentage availability
- [ ] Availability by observing run
- [ ] Availability by source class
- [ ] Availability by Circular type
- [ ] Typical uncertainty when reported

## M5.2 — Direct vs approximated quantities

Maintain a table:

```yaml
parameter:
directly_available: true|false|sometimes
source:
required_for_method:
approximation_if_missing:
scientific_risk:
```

## M5.3 — Additional discoveries

Reserve this section deliberately.

- [ ] Identify correlations not originally planned.
- [ ] Identify useful parameters beyond chirp mass.
- [ ] Record potential secondary scientific questions.
- [ ] Record unexpected data-quality issues.
- [ ] Decide whether any discovery deserves thesis inclusion.

### Exit criteria

We know empirically what the Circular dataset can and cannot support.

---

# MILESTONE 6 — Chirp-Mass Method: Physics Verification

**Goal:** Convert the working-note approximation into a scientifically defensible experimental method—or reject/modify it if necessary.

**Status:** `TODO`

## M6.1 — Re-derive equation

Starting concept:

```text
SNR relation
-> chirp-mass amplitude dependence
-> orientation dependence
-> detector noise integral
-> rearrangement for redshifted chirp mass
-> source-frame conversion
```

- [ ] Derive each step independently.
- [ ] Attach citation to literature-derived equations.
- [ ] Check dimensions/units.
- [ ] Distinguish proportionality from equality.
- [ ] Verify treatment of redshift.
- [ ] Verify luminosity-distance units.

## M6.2 — Investigate assumptions

### SNR

- [ ] Determine how often SNR is directly available.
- [ ] Do not infer SNR from FAR without justification.
- [ ] Test consequences of assumed SNR ranges.

### Orientation

- [ ] Verify correct distribution of inclination/orientation.
- [ ] Test fixed-average approximation.
- [ ] Test Monte Carlo orientation marginalization if feasible.

### Detector response / noise integral

- [ ] Determine whether treating it as constant is defensible.
- [ ] Test observing-run dependence.
- [ ] Test detector-network dependence.
- [ ] Consider calibration stratified by observing run/network.

### Calibration constant C

- [ ] Reproduce previous C calculation.
- [ ] Avoid single-event calibration if possible.
- [ ] Fit C using training events.
- [ ] Hold out validation events.
- [ ] Estimate uncertainty in C.
- [ ] Test systematic bias.

## M6.3 — Alternative models

Leave room for models discovered during analysis.

Possible tests:

- [ ] Baseline scaling estimator
- [ ] Run-specific calibration
- [ ] Source-class-specific calibration
- [ ] Regression baseline
- [ ] Bayesian/Monte Carlo approximation
- [ ] Simple ML regression if dataset size and scientific justification permit

### Decision gate

At the end of M6 classify the chirp-mass work as one of:

```yaml
status: validated_approximation | useful_constraint | exploratory_only | unsupported
```

Do **not** force a positive result.

---

# MILESTONE 7 — Historical Back-testing and Validation

**Goal:** Determine whether the method generalizes beyond calibration events.

**Status:** `TODO`

## M7.1 — Experimental split

- [ ] Define calibration/training set.
- [ ] Define validation set.
- [ ] Keep catalog truth hidden from estimator inputs.
- [ ] Document selection criteria.

## M7.2 — Run estimator

For every validation event record:

```yaml
event_id:
observing_run:
inputs_available:
inputs_approximated:
estimated_chirp_mass:
estimated_uncertainty:
catalog_chirp_mass:
absolute_error:
relative_error:
source_class:
failure_reason:
```

## M7.3 — Statistical evaluation

- [ ] MAE
- [ ] Median absolute error
- [ ] Relative/percentage error
- [ ] RMSE if appropriate
- [ ] Bias
- [ ] Error distribution
- [ ] Performance by source class
- [ ] Performance by observing run
- [ ] Performance vs distance
- [ ] Performance vs SNR, where available
- [ ] Coverage of uncertainty interval, if uncertainty model exists

## M7.4 — Required plots

- [ ] Estimated vs catalog chirp mass scatter plot
- [ ] Ideal `y=x` reference
- [ ] Residual/error plot
- [ ] Error histogram
- [ ] Relative error by event
- [ ] Error vs luminosity distance
- [ ] Error vs SNR
- [ ] Performance by observing run
- [ ] Performance by source class
- [ ] Calibration sensitivity plot

## M7.5 — Baseline comparison

Compare against simple alternatives where scientifically meaningful:

- [ ] Source-class midpoint baseline
- [ ] Population-average baseline
- [ ] Simple regression baseline
- [ ] Existing rapid-estimation approach from literature, if comparable

### Exit criteria

We can answer quantitatively whether the estimator adds information beyond trivial baselines.

---

# MILESTONE 8 — Apply to Current / Pre-Catalog Events

**Goal:** Demonstrate the intended early-information use case without overstating predictions.

**Status:** `TODO`

- [ ] Select events with sufficient inputs.
- [ ] Apply only the frozen method developed using historical data.
- [ ] Record assumptions per event.
- [ ] Produce preliminary estimates/ranges.
- [ ] Clearly label these as experimental estimates.
- [ ] Compare later if authoritative parameter estimates become available.
- [ ] Maintain a prediction log with timestamps/versioning where useful.

### Potential output table

| Event | Circular date | Available inputs | Assumptions | Estimated mass/range | Later reference | Status |
|---|---|---|---|---|---|---|

---

# MILESTONE 9 — GW-Pathfinder System

**Goal:** Build the intelligent-access layer over reliable GW data and project outputs.

**Status:** `TODO`

## M9.1 — Define supported questions

Examples:

- [ ] Explain GW terminology.
- [ ] Retrieve event parameters.
- [ ] Search events by physical criteria.
- [ ] Compare events.
- [ ] Explain source classifications.
- [ ] Retrieve Circular-derived information.
- [ ] Show provenance/source for values.
- [ ] Explain experimental chirp-mass estimate and limitations.

## M9.2 — Data architecture

Possible architecture:

```text
GW catalogs -----------\
                        -> normalized data layer -> retrieval/query layer -> GW-Pathfinder UI
GCN Circular pipeline -/
                                      |
                                      -> scientific analysis / estimator
```

- [ ] Define normalized schema.
- [ ] Decide SQL/DataFrame/vector DB roles.
- [ ] Avoid embeddings for tasks better handled by structured queries.
- [ ] Use retrieval for literature/explanatory text where useful.
- [ ] Require provenance for scientific values.

## M9.3 — Conversational layer

- [ ] Implement minimal working interface.
- [ ] Connect structured query capability.
- [ ] Connect retrieval where required.
- [ ] Prevent unsupported numerical hallucination.
- [ ] Return source/provenance.
- [ ] Add limitation statements for experimental inference.

## M9.4 — Chatbot evaluation

Create test-question categories:

```yaml
factual_retrieval:
comparison:
filtering:
definition:
circular_query:
scientific_interpretation:
out_of_scope:
```

Evaluate:

- [ ] Correctness
- [ ] Retrieval accuracy
- [ ] Numerical fidelity
- [ ] Citation/provenance correctness
- [ ] Hallucination rate
- [ ] Response usefulness

### Thesis outputs

- [ ] System architecture figure
- [ ] Interface screenshots
- [ ] Query examples
- [ ] Evaluation table
- [ ] Failure examples

---

# MILESTONE 10 — Integration / Demonstrator

**Goal:** Show that the components form one project rather than disconnected experiments.

**Status:** `TODO`

Target demonstrator:

```text
Select/Search GW Event
        |
        +-> Catalog information
        |
        +-> Associated GCN Circular(s)
        |
        +-> Automatically extracted parameters
        |
        +-> Explain parameters
        |
        +-> Run experimental early chirp-mass analysis (where applicable)
        |
        +-> Compare with catalog/reference value (historical events)
```

- [ ] Implement one end-to-end path first.
- [ ] Use a small reliable event set before scaling.
- [ ] Add error handling.
- [ ] Add provenance display.
- [ ] Add visualizations.
- [ ] Add clear distinction between reported and inferred values.

This demonstrator can also support a practical college exhibition if needed.

---

# MILESTONE 11 — Thesis Figures, Tables, and Evidence Package

**Goal:** Ensure every important thesis claim is backed by an artifact.

**Status:** `TODO`

## Figures to consider

- [ ] Overall thesis/project architecture
- [ ] GW data ecosystem diagram
- [ ] GW-Pathfinder architecture
- [ ] GCN processing pipeline
- [ ] Dataset filtering flow
- [ ] Parameter availability chart
- [ ] Missing-data heatmap
- [ ] Literature/comparative landscape figure
- [ ] Chirp-mass method schematic
- [ ] Estimated vs true mass
- [ ] Residual/error distributions
- [ ] Calibration analysis
- [ ] Performance by observing run
- [ ] Performance by source class
- [ ] Interface screenshots
- [ ] End-to-end event example

## Tables to consider

- [ ] Literature comparison
- [ ] Data sources
- [ ] Extracted Circular fields
- [ ] Direct vs approximated quantities
- [ ] Dataset statistics
- [ ] Extraction evaluation
- [ ] Calibration events
- [ ] Validation events
- [ ] Chirp-mass results
- [ ] Baseline comparison
- [ ] Chatbot evaluation
- [ ] Limitations

## Reproducibility artifacts

- [ ] `requirements.txt` or environment file
- [ ] README
- [ ] Data dictionary
- [ ] Processing instructions
- [ ] Experiment configuration
- [ ] Versioned results
- [ ] Git commit/version associated with thesis results

---

# MILESTONE 12 — Thesis Writing

**Goal:** Produce the thesis continuously rather than after implementation.

**Status:** `IN_PARALLEL`

## Chapter 1 — Introduction

- [ ] GW astronomy context
- [ ] Information-access challenge
- [ ] Motivation for computational/AI support
- [ ] Problem statement
- [ ] Research questions
- [ ] Objectives
- [ ] Contributions
- [ ] Thesis organization

## Chapter 2 — Research Background / Literature Review

- [ ] GW detection and parameter estimation basics
- [ ] GW data/catalog infrastructure
- [ ] Low-latency alerts and GCN
- [ ] AI/ML in GW astronomy
- [ ] NLP/LLM/scientific information systems
- [ ] Existing related tools
- [ ] Related transient/circular studies
- [ ] Research gap

## Chapter 3 — Project Evolution and System Design

- [ ] Original GW-Pathfinder motivation
- [ ] Why the project expanded toward Circular processing
- [ ] Unified architecture
- [ ] Design requirements
- [ ] Scope

## Chapter 4 — Data and Circular Pipeline

- [ ] Data sources
- [ ] Acquisition
- [ ] Filtering
- [ ] Event matching
- [ ] Parameter extraction
- [ ] Data cleaning
- [ ] Dataset statistics
- [ ] Extraction evaluation

## Chapter 5 — Scientific Case Study / Methodology

- [ ] Chirp-mass physics
- [ ] Literature-derived equations
- [ ] Proposed approximation
- [ ] Assumptions
- [ ] Calibration
- [ ] Experimental design
- [ ] Baselines
- [ ] Metrics

## Chapter 6 — GW-Pathfinder Implementation

- [ ] Architecture
- [ ] Data layer
- [ ] Retrieval/query system
- [ ] Conversational interface
- [ ] Integration with Circular pipeline
- [ ] Safety/reliability/provenance mechanisms

## Chapter 7 — Results

- [ ] Extraction results
- [ ] Dataset findings
- [ ] Parameter availability
- [ ] Historical validation
- [ ] Chirp-mass performance
- [ ] Baseline comparison
- [ ] Current-event application, if appropriate
- [ ] GW-Pathfinder evaluation

## Chapter 8 — Discussion

- [ ] What worked
- [ ] What did not work
- [ ] Interpretation
- [ ] Scientific usefulness
- [ ] Bias
- [ ] Data limitations
- [ ] Approximation limitations
- [ ] Generalizability
- [ ] Relationship to existing work

## Chapter 9 — Conclusion and Future Work

- [ ] Main contribution
- [ ] Answers to research questions
- [ ] Thesis-level achievement
- [ ] Paper-level extensions
- [ ] Better calibration
- [ ] Larger datasets
- [ ] Additional inferred parameters
- [ ] Better NLP/extraction
- [ ] Deeper GW-Pathfinder integration

---

# MILESTONE 13 — Final Scientific and Technical Review

**Status:** `TODO`

## Scientific checks

- [ ] Every equation has a source or is explicitly identified as our derivation.
- [ ] Every assumption is disclosed.
- [ ] Estimated values are not presented as measured values.
- [ ] Calibration and validation data are separated.
- [ ] No data leakage.
- [ ] Error metrics are correctly calculated.
- [ ] Negative results are reported honestly.
- [ ] Claims match evidence.

## Code checks

- [ ] Clean run from raw/intermediate data to final results.
- [ ] Fix random seeds where appropriate.
- [ ] Remove unused code.
- [ ] Remove credentials/private information.
- [ ] Document dependencies.
- [ ] Confirm figures can be regenerated.

## Thesis checks

- [ ] Consistent terminology.
- [ ] Consistent event names.
- [ ] Consistent units.
- [ ] All figures referenced.
- [ ] All tables referenced.
- [ ] All citations present.
- [ ] No unsupported statements.
- [ ] Abstract matches final work rather than original plan.

---

# MILESTONE 14 — Submission Package

**Status:** `TODO`

- [ ] Final thesis PDF
- [ ] LaTeX source
- [ ] Bibliography/BibTeX
- [ ] Final figures
- [ ] Final tables
- [ ] Clean code repository
- [ ] README
- [ ] Data dictionary
- [ ] Reproduction instructions
- [ ] Demonstration screenshots/video if required
- [ ] Presentation/slides if required
- [ ] Supervisor review corrections

---

# MILESTONE 15 — Post-Thesis Paper Continuation

**Status:** `FUTURE`

Potential directions, dependent on thesis results:

- [ ] Expand historical validation sample.
- [ ] Extend O4 analysis.
- [ ] Validate predictions when authoritative results become available.
- [ ] Improve detector/run-dependent calibration.
- [ ] Develop uncertainty-aware estimator.
- [ ] Explore additional parameters inferable from Circulars.
- [ ] Compare physics-based estimator with statistical/ML alternatives.
- [ ] Improve automated Circular extraction.
- [ ] Integrate live/near-live alert processing if feasible.
- [ ] Expand GW-Pathfinder into a research assistant rather than only a chatbot.
- [ ] Prepare publication-quality statistical analysis.
- [ ] Identify precise paper research question based on actual thesis findings.

---

# Dynamic Research Backlog

> Add discoveries here without immediately changing the core thesis.

```yaml
- id: DISC-001
  idea: null
  source: literature|data|code|supervisor|analysis
  scientific_value: null
  effort: low|medium|high
  thesis_relevance: low|medium|high
  decision: pending|include|future|reject
  notes: null
```

---

# Risk Register

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Existing code does not run | High | Audit immediately; salvage components before rebuilding |
| R2 | Circulars lack required estimator inputs | High | Perform parameter-availability study early |
| R3 | Chirp-mass approximation is scientifically weak | High | Back-test; compare baselines; reframe as exploratory/constraint if needed |
| R4 | Too much time spent on chatbot UI | High | Build minimum interface only after data pipeline works |
| R5 | Thesis scope grows continuously | High | Put new ideas in Dynamic Research Backlog before inclusion |
| R6 | Writing postponed | High | Update thesis every day alongside technical work |
| R7 | Results in old notes cannot be reproduced | Medium/High | Treat them as unverified until regenerated |
| R8 | Literature changes project direction | Medium | Maintain versioned thesis skeleton and revise based on evidence |

---

# Immediate Execution Order

The first practical sequence should be:

```text
1. Inventory files/code/data
2. Run existing code
3. Establish reproducible development environment
4. Recover GCN extraction pipeline
5. Inspect actual extracted dataset
6. Build/verify catalog reference dataset
7. Quantify Circular parameter availability
8. Verify chirp-mass physics and assumptions
9. Construct historical back-test dataset
10. Calibrate without validation leakage
11. Validate and generate plots/tables
12. Decide scientific strength of estimator
13. Apply to appropriate current/O4 data
14. Build minimum GW-Pathfinder interface around reliable data
15. Evaluate interface
16. Integrate demonstrator
17. Complete thesis evidence package
18. Final scientific review
19. Submission
20. Continue strongest result toward paper
```

---

# Definition of a Successful Bachelor's Thesis

The project does **not** require every future idea to work. A successful thesis should demonstrate:

- [ ] A clearly motivated GW research problem.
- [ ] A defensible literature/research background.
- [ ] A reproducible GW/GCN data-processing pipeline.
- [ ] A structured dataset or substantial data product.
- [ ] Quantitative evaluation of extraction quality.
- [ ] At least one scientifically meaningful analysis/case study.
- [ ] Honest validation and limitations of the chirp-mass investigation.
- [ ] A functional GW-Pathfinder component demonstrating intelligent access to the data/workflow.
- [ ] Figures, tables, metrics, and reproducible evidence.
- [ ] A clear distinction between thesis contribution and future paper work.

---

# Current Next Action

```yaml
next_milestone: M1
next_task: M1.1
action: "Recover and inventory all existing project code, datasets, notes, literature, and outputs before modifying the implementation."
status: TODO
```
