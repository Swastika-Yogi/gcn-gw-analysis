# GW Pathfinder

Chirp-mass estimation and AI-assisted analysis of gravitational-wave GCN circulars. Bachelor's thesis project — see `docs/GW_Thesis_Master_Plan.md` for the full 15-milestone plan and `docs/GW_PROJECT_CONTEXT_FOR_CLAUDE.md` for the original scope/methodology brief.

Author: Swastika Yogi

## What's here

The repo is organized around the thesis's three legs, plus a `shared/` layer for the pipeline both Leg 1 and Leg 3 depend on:

- `shared/` — ingestion, parsing, processing: downloads the circular archive, filters to GW-related circulars, extracts event IDs/distance/FAR/classification/chirp-mass with provenance, builds a structured event table. Used by both Leg 1 and (once built) Leg 3.
- `legs/leg1_estimation/` — the chirp-mass estimation work: `modeling/` (physics + statistical estimators, calibration, baselines), `validation/`, `analysis/`, entry points `run_pipeline.py` and `validate_estimator.py`, its `data/processed/` outputs, and `docs/feasibility_draft.md`.
- `legs/leg2_ai_comparison/` — AI-model reliability study (placeholder as of 2026-08-20; code/data land here starting Day 6 of the sprint).
- `legs/leg3_pathfinder/` — the GW Pathfinder retrieval-grounded query tool: `docs/pathfinder_design_draft.md` (architecture) now, embedding/retrieval code from Day 8 of the sprint.
- `docs/` — governing/aggregate documents only: the master plan, the original project-context brief, and the whole-thesis overview draft.
- `project_inventory.md`, `code_audit.md` — M1 audit deliverables.

**Entry points run as modules from the repo root** (not as bare scripts), since they import from the top-level `legs`/`shared` packages:
```
python3 -m legs.leg1_estimation.run_pipeline
python3 -m legs.leg1_estimation.validate_estimator
```

Current verified numbers (see `docs/feasibility_draft.md` for full results): 181 O4a events identified, 89%/46%/45%/0% coverage for distance/FAR/classification/reference-chirp-mass. (Earlier notes in this README claimed ~150 events and ~70 usable — those were unverified and are now superseded; see `code_audit.md` for how the real counts were reproduced.)

## Changelog

Dated, one-line-per-change log — kept terse on purpose. For the fuller day-by-day story (what was hard, what's still open, what needs supervisor input), see `docs/progress_log.md`. Newest first.

- **2026-08-22** — `M6.3`: run-specific calibration (`legs/leg1_estimation/validate_run_stratified_calibration.py`) on the 214-event catalog-backed set — fitting C separately per observing-run era (O3 vs. O4) cuts real-SNR median error from 31.5% to 26.6%. Fine-grained per-run splits get the same average result but are unstable on the two smaller runs (O3a n=25, O3b n=18); era-level is the version kept.
- **2026-08-22** — `M5.2`/`M5.3`: direct-vs-approximated-quantities table and additional-discoveries write-up in `feasibility_draft.md`/LaTeX — flags network SNR as the one "High risk" missing parameter, and records a new, currently-unused parameter found along the way: sky-localization area, present in 299/505 events (59.2%).
- **2026-08-22** — `M4.4`: manual gold-sample audit (`legs/leg1_estimation/analysis/gold_sample_audit.py`, 45 hand-annotated circulars) — all four field parsers scored perfect precision/recall/F1, but the audit process itself caught and fixed a real bug: `far_parser.py` misread ordinary English ("so far", "as far as") as a fabricated FAR value due to a missing word boundary. Fixed, verified no coverage regression.
- **2026-08-22** — `M5.1`: full availability breakdown by observing run/source class/circular type (`legs/leg1_estimation/analysis/availability_analysis.py`) — added real O3a/O3b/O4b/O4c date windows (previously only O4a was defined). Key finding: the reference-chirp-mass bin sentence is completely absent before O4c (0/400 events) and present in 58.6% of O4c events, not just "rare overall" as previously stated.
- **2026-08-22** — GWTC catalog integration (`legs/leg1_estimation/validation/{load_reference_catalog,match_events}.py`, `validate_against_catalog.py`): GWOSC's `gracedb_id` field is the exact circular `S`-ID for post-2019 events. Built a 214-event validation set (circular distance + real catalog chirp mass + real SNR) — **swapping assumed SNR=15 for the real value cuts median error from 46.6% to 31.5%**, a direct, controlled confirmation that SNR is the dominant error source. 153 catalog events have no matching circular in our archive: confirmed this is because they're low-significance (median FAR 3/yr vs 1e-5/yr for matched events) — offline/retrospective catalog additions that never triggered a real-time public alert, not a pipeline bug or stale archive.
- **2026-08-22** — FAR→SNR proxy (`validate_far_snr_proxy.py`, `validate_far_proxy_estimator.py`): reversed the earlier "FAR is a weak proxy" finding (r≈−0.34 on 49 back-solved events) by testing directly against 381 real (SNR,FAR) catalog pairs — r=−0.70, 10.7% median SNR error. Applied downstream to the circular-only set, gain is real but modest (44.8%→39.5%), traced to those events sitting in a harder-to-predict FAR range, not a flaw in the proxy.
- **2026-08-22** — Combined class+distance model, revisited (`validate_combined_class_distance.py`) on the 214-event catalog-backed set (206 BBH/5 NSBH/2 Terrestrial/1 BNS — real diversity, unlike the old 49-event set that forced this to be rejected). Clean result: distance alone (27.8% median) beats class alone (38.5%) and combining adds nothing (28.9%). Bonus: distance-only at this scale is now competitive with the physics formula's real-SNR result (31.5%).
- **2026-08-22** — Wrote the catalog-validation finding, the missing-events investigation, the FAR→SNR proxy result, and the corrected baseline explanation into the actual thesis documents: `feasibility_draft.md` (new Section 6), the LaTeX Results/Conclusion/Introduction chapters, and the abstract.
- **2026-08-22** — Corrected an overstated claim in `feasibility_draft.md`/the LaTeX Results chapter: the "trivial baseline is competitive" finding was attributed to a distance-class correlation, but the validation set is 98% one class (48/49 BBH) — not enough diversity to support that explanation. Rewritten to say what the data actually shows.
- **2026-08-20** — `M7.4`: added `legs/leg1_estimation/generate_plots.py` (needs the `.venv` + `matplotlib`, see `requirements.txt`) — 12 validation plots (scatter/residual/histogram/error-vs-distance × 3 estimators). Confirmed visually what the numbers already showed: uncalibrated physics error rises sharply with distance (up to ~700%), calibration compresses but doesn't remove that trend (~400%), and the statistical model's reference values show clear discrete banding from the bin-quantized ground truth.
- **2026-08-20** — Added `docs/progress_log.md` (detailed daily record) and five reference notes under `docs/references/`; deleted the stale pre-fix `.\o4a_gw_dataset.csv`.
- **2026-08-20** — Added a LaTeX thesis skeleton (`thesis/latex/`) matching the Tribhuwan University template structure; real research content in Chapters 1/3/4/5, institutional front-matter left `TODO`.
- **2026-08-20** — Restructured the repo into `shared/` + `legs/{leg1_estimation,leg2_ai_comparison,leg3_pathfinder}/`, one folder per thesis leg plus the pipeline they share. Entry points now run as modules (`python3 -m legs.leg1_estimation.run_pipeline`); confirmed identical output to before the move.
- **2026-08-20** — Environment audit: confirmed direct `pip install` is blocked (PEP 668) but works via a venv; no LLM API key configured (needed before the Pathfinder prototype, planned ~Day 8-9).
- **2026-08-20** — `M1`: wrote `project_inventory.md` and `code_audit.md`; found the governing plan documents only existed as pasted chat content and saved them to `docs/`.
- **2026-08-20** — `M7.5`: added two trivial baselines (`legs/leg1_estimation/modeling/baselines.py`) — found the source-class-midpoint baseline is competitive with the statistical model on several metrics, now documented as an explicit caveat in `legs/leg1_estimation/docs/feasibility_draft.md`.
- **2026-08-20** — `M7.3`: added MAE/RMSE/bias to `legs/leg1_estimation/validation/metrics.py`.
- **2026-08-20** — `M6.2`: properly fit and validated the physics formula's calibration constant C (`legs/leg1_estimation/modeling/calibration.py`, leave-one-out, no leakage). Median error improved 115%→45%, but a residual bias (r=0.55 with distance) survives calibration — evidence the shortfall is structural, not a bad constant.
- **2026-08-19** — Built the 49-event validation set (all runs, self-reported reference chirp mass) and the statistical (distance-only) estimator; found it outperforms the physics formula (33% vs 115% median error).
- **2026-08-19** — Restructured the original single-file `gcn_analysis.py` into the modular `src/` layout; deleted the superseded script.
- **2026-08-19** — Fixed the event-ID regex (was silently dropping multi-letter-suffix events — O4a count went 79→181) and the classification regex (was missing `>99%` format, corrupting `source_class`).
- **2026-08-19** — Fixed the original mass/distance/FAR extraction regexes, which were too strict (fixed keyword-to-number character window) and were producing near-zero usable circulars.
