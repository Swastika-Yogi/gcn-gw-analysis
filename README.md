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
