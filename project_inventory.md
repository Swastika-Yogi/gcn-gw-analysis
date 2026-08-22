# Project Inventory

> Deliverable for Master Plan M1.1. Compiled 2026-08-20 from direct inspection of the repository plus prior conversation history (documents/screenshots shared but not yet saved as files are noted as `external`).

## Code

```yaml
- name: shared/ingestion/load_gcn_archive.py
  type: code
  location: shared/ingestion/load_gcn_archive.py
  purpose: Download/cache the GCN circular archive tarball; load all circulars into memory.
  status: working
  last_known_result: "45,268 circulars loaded"
  dependencies: [requests]
  needs_review: false

- name: shared/parsing/event_id_parser.py
  type: code
  location: shared/parsing/event_id_parser.py
  purpose: Extract LVK superevent IDs (SYYMMDDx) and screen circulars for GW relevance.
  status: working
  last_known_result: "Regex originally missed multi-letter suffixes; fixed 2026-08-19, O4a event count went 79 -> 181"
  dependencies: []
  needs_review: false

- name: shared/parsing/mass_parser.py
  type: code
  location: shared/parsing/mass_parser.py
  purpose: Extract chirp-mass bin sentence and a lower-confidence generic mass mention.
  status: working
  last_known_result: "Bin sentence extraction validated against 54 archive-wide matches, 0 in O4a"
  dependencies: []
  needs_review: false

- name: shared/parsing/distance_parser.py
  type: code
  purpose: Extract luminosity distance, with uncertainty when reported as mean +/- error.
  status: working
  needs_review: false

- name: shared/parsing/far_parser.py
  type: code
  purpose: Extract false alarm rate and unit.
  status: working
  needs_review: false

- name: shared/parsing/classification_parser.py
  type: code
  purpose: Extract BBH/BNS/NSBH/Terrestrial probabilities and derive source_class.
  status: working
  last_known_result: "Regex originally missed '>99%' format, corrupting labels; fixed 2026-08-19"
  needs_review: false

- name: shared/parsing/snr_parser.py
  type: code
  purpose: Deliberate no-op - network SNR is not reliably present in circulars (see docstring).
  status: working
  needs_review: false

- name: shared/processing/group_by_event.py
  type: code
  purpose: Group circulars by event ID, optional run-window filter (e.g. O4a).
  status: working
  needs_review: false

- name: shared/processing/build_event_table.py
  type: code
  purpose: Combine parsers into one event-level table with provenance logging.
  status: working
  needs_review: false

- name: legs/leg1_estimation/modeling/chirp_mass_estimator.py
  type: code
  purpose: Physics (SNR-scaling) chirp-mass formula from the methodology note.
  status: working
  needs_review: false

- name: legs/leg1_estimation/modeling/statistical_estimator.py
  type: code
  purpose: Generic log-linear least-squares fit/predict (no numpy dependency).
  status: working
  needs_review: false

- name: legs/leg1_estimation/modeling/apply_estimator.py
  type: code
  purpose: Applies the physics estimator with fixed assumed snr/cos_iota/C to an event table.
  status: working
  needs_review: false

- name: legs/leg1_estimation/modeling/calibration.py
  type: code
  purpose: Fit and validate the physics formula's calibration constant C (M6.2) via leave-one-out; bias test.
  status: working
  last_known_result: "Fitted C ~5.6e-5 vs methodology note's 1e-4; residual bias r=0.55 with distance even after fitting"
  needs_review: false

- name: legs/leg1_estimation/modeling/baselines.py
  type: code
  purpose: Trivial baselines for M7.5 (source-class midpoint, population average).
  status: working
  last_known_result: "Class-midpoint baseline competitive with the statistical model on several metrics - see legs/leg1_estimation/docs/feasibility_draft.md Section 6"
  needs_review: false

- name: legs/leg1_estimation/validation/build_validation_set.py
  type: code
  purpose: Build the validation set of events with self-reported reference chirp mass, all runs.
  status: working
  needs_review: false

- name: legs/leg1_estimation/validation/metrics.py
  type: code
  purpose: percent_error, bin_hit, leave-one-out CV runner, summarize() (median/MAE/RMSE/bias/bin-hit).
  status: working
  needs_review: false

- name: legs/leg1_estimation/analysis/reports.py
  type: code
  purpose: Data-availability report (Experiment A) for an event table.
  status: working
  needs_review: false

- name: legs/leg1_estimation/run_pipeline.py
  type: code
  purpose: Entry point - builds the O4a event table end to end. Run as `python3 -m legs.leg1_estimation.run_pipeline` from repo root.
  status: working
  last_known_result: "181 O4a events; 89% distance, 46% FAR, 45% classification, 0% reference chirp mass"
  needs_review: false

- name: legs/leg1_estimation/validate_estimator.py
  type: code
  purpose: Entry point - compares physics/calibrated-physics/statistical/baseline estimators on the 49-event validation set. Run as `python3 -m legs.leg1_estimation.validate_estimator` from repo root.
  status: working
  last_known_result: "See legs/leg1_estimation/docs/feasibility_draft.md Section 6 for the full results table"
  needs_review: false

- name: gcn_analysis.py
  type: code
  location: "deleted 2026-08-19 (git history: commit cec586b3)"
  purpose: Original single-file script - superseded entirely by src/ + run_pipeline.py.
  status: obsolete
  needs_review: false
```

## Datasets

```yaml
- name: jsons/archive.json/
  type: dataset
  location: jsons/archive.json/
  purpose: Raw circular JSON files, one per circular ID.
  status: working
  last_known_result: "45,268 files; grows on each re-download since the live GCN archive is appended to"
  dependencies: [shared/ingestion/load_gcn_archive.py]
  needs_review: false

- name: legs/leg1_estimation/data/processed/o4a_event_table.csv
  type: dataset
  purpose: Structured O4a event table, output of run_pipeline.py.
  status: working
  needs_review: false

- name: legs/leg1_estimation/data/processed/validation_results.csv
  type: dataset
  purpose: Per-event predictions from all four estimators/baselines, output of validate_estimator.py.
  status: working
  needs_review: false

- name: ./o4a_gw_dataset.csv
  type: dataset
  location: "repo root (Windows-style leading backslash in filename)"
  purpose: Output of the now-deleted gcn_analysis.py.
  status: obsolete
  needs_review: true
  notes: "Stale artifact of the pre-fix pipeline (7 usable events, before the ID/classification regex fixes). Should be deleted or clearly marked historical - currently just sitting in the repo root looking like a current output."
```

## Thesis documents

```yaml
- name: docs/GW_PROJECT_CONTEXT_FOR_CLAUDE.md
  type: note
  purpose: Original project-context brief (scope, formula, warnings, expected schema).
  status: working
  needs_review: false

- name: docs/GW_Thesis_Master_Plan.md
  type: note
  purpose: The governing 15-milestone plan this inventory is a deliverable of.
  status: working
  needs_review: false

- name: legs/leg1_estimation/docs/feasibility_draft.md
  type: note
  purpose: Thesis draft - data availability, both estimators, calibration, validation results, decision-gate classification.
  status: working
  needs_review: false

- name: docs/thesis_overview_draft.md
  type: note
  purpose: One-page thesis overview / abstract-style draft covering all three project legs.
  status: working
  needs_review: false

- name: legs/leg3_pathfinder/docs/pathfinder_design_draft.md
  type: note
  purpose: GW Pathfinder architecture (design-only as of 2026-08-20; a minimal build is planned Days 8-10 of the sprint).
  status: partial
  needs_review: false
```

## Reference notes (extracted text, saved 2026-08-20 - see docs/references/)

These were shared as PDFs in conversation; only their extracted text is saved here, not the original PDF bytes (not reconstructable from what was received). If the original PDF files matter for submission, add them to this folder directly.

```yaml
- name: docs/references/chirp-mass-methodology-note.md
  type: note
  location: docs/references/chirp-mass-methodology-note.md
  purpose: Methodology note - source of the SNR-scaling chirp-mass formula.
  status: working
  needs_review: true
  notes: "Not a peer-reviewed source; M6.1 asks to attach a citation to literature-derived equations, which this doesn't have."

- name: docs/references/ai-model-comparison-report.md
  type: note
  location: docs/references/ai-model-comparison-report.md
  purpose: AI-model comparison study (Leg 2) - RTCROS prompting framework, initial 5-model results.
  status: working
  needs_review: false

- name: docs/references/concept-object-associations-note.md
  type: note
  location: docs/references/concept-object-associations-note.md
  purpose: Literature note on a knowledge-graph/ALS paper - evaluated and explicitly NOT adopted for GW Pathfinder.
  status: working
  needs_review: false

- name: docs/references/posterior-inference-note.md
  type: note
  location: docs/references/posterior-inference-note.md
  purpose: Literature note on retrieval + local-refinement posterior inference - evaluated, judged out of scope for this thesis's timeline.
  status: working
  needs_review: false

- name: docs/references/gw-physics-background-talk.md
  type: note
  location: docs/references/gw-physics-background-talk.md
  purpose: GW physics background slide deck notes (Naresh Adhikari, FTCC) - candidate Ch.2 background material.
  status: working
  needs_review: false
```

## Still external (not saved as repo files)

```yaml
- name: "Coding-for-beginners reading list, GW GCN Reader todo notes (screenshots)"
  type: note
  location: external
  purpose: User's own personal planning notes - some fields listed (event_time, detector count) aren't in the current pipeline yet.
  status: unknown
  needs_review: true
```

## Published artifacts (claude.ai-hosted, private)

```yaml
- name: Chirp Mass Feasibility memo
  type: figure
  location: https://claude.ai/code/artifact/28266fbe-bc5f-4a11-9d3a-3ae38466ec45
  purpose: Supervisor-facing memo on the SNR-sensitivity/calibration finding.
  status: working
  needs_review: false

- name: GW Pathfinder overview
  type: figure
  location: https://claude.ai/code/artifact/9b72bcb7-576b-41ee-a69d-e16db88fe066
  purpose: Full three-leg project overview for supervisor/collaborator review.
  status: working
  needs_review: false

- name: Fourteen Days, Full Thesis
  type: figure
  location: https://claude.ai/code/artifact/f8ca5ba2-87a5-48f4-bbec-4a889b384ed3
  purpose: Day-by-day sprint plan to the 2026-09-02 deadline.
  status: working
  needs_review: false
```

## Not yet started

```yaml
- name: literature_database.md
  type: other
  purpose: Per-plan M2.2 structured literature entries.
  status: unknown
  needs_review: true
  notes: "Scheduled Day 4 of the sprint."

- name: code_audit.md
  type: other
  purpose: Per-plan M1.2 - see companion file, written alongside this inventory.
  status: working
```
