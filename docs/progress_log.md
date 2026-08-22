# Progress Log

Detailed daily record, separate from `README.md`'s terse one-line-per-change changelog. Each entry: what got done, what was harder than expected or genuinely surprising, what's still open, and anything worth raising with the supervisor. Written at the end of each working day.

---

## 2026-08-22 (Day 2 of the sprint)

### What we did

- **M7.4** — built `generate_plots.py`, producing scatter, residual, error-histogram, and error-vs-distance plots for all three estimators. Confirmed by eye that they show exactly what the numbers already implied, plus one new finding not previously checked: the statistical model's error does *not* rise with distance the way the physics formula's does, evidence its shortcomings are a genuinely different kind of problem.
- **Traced the two worst-outlier events by hand**, in response to a real worry that error this high might mean the pipeline itself was broken. Went back to the raw circular text for both. Result: extraction was accurate in both cases (one even correctly picked up a *revised* distance value from a later circular instead of a stale initial one) — the large errors trace cleanly to the SNR assumption, not to a data problem.
- **"Do we need better calibration?" — answered no.** The fitted C is already stable to within ~0.3% across folds; the remaining error is a structural bias no single constant can absorb. Recommended extending the statistical model instead.
- **GWTC catalog integration authorized and started.** Rather than waiting on the supervisor's response, we're bringing in the public GWTC catalog (GWOSC) as an additional reference source, with the understanding that this can be revised if the supervisor later has concerns.
- Built `load_reference_catalog.py`, `match_events.py`, `validate_against_catalog.py`. Discovered the ID crosswalk: GWOSC's per-event `gracedb_id` field *is* the exact circular `S`-ID for any event from 2019 onward (verified directly against S230627c).
- This immediately paid off: the catalog gives **real chirp mass (6.02 M☉) and real network SNR (28.7)** for S230627c — an O4a event whose circulars report no chirp mass at all. This is the first point in the project where the physics formula can be tested against a real SNR instead of an assumed one.
- **Result: the core hypothesis is now directly confirmed, not just argued.** Cross-matched 227 catalog events to circulars (153 more recent events aren't in our circular archive yet — see below; 11 pre-2019 events use an older ID scheme and are out of scope). Built a 214-event combined set (>4x the old 49-event validation set) with circular-extracted distance and catalog-provided real chirp mass and real SNR. Same formula, same distance, same C-fitting method — only the SNR input changes: **real SNR gives 31.5% median error (89/214 within ±25%); assumed SNR=15 gives 46.6% median error (58/214 within ±25%).** Supplying the real SNR alone — nothing else changed — cuts the error by a third. This is a controlled, direct confirmation that SNR really was the dominant missing variable, not just a plausible theoretical argument.

### Rejected / walked back — worth keeping on record

- **Combined class+distance statistical model.** Proposed as the natural next step to improve on the distance-only model. Abandoned immediately on checking the data: 48 of the 49 validation events are BBH — there's no real class diversity to model, so building this would mean drawing a conclusion from essentially one data point. Better to not build something that looks rigorous but isn't.
- **Corrected an already-written claim.** `feasibility_draft.md` and the LaTeX Results chapter previously explained the "trivial baseline is competitive" finding as evidence that distance and source class are correlated. That's overstated — with almost no class diversity in the sample, the baseline's competitiveness is really just "guessing the sample's most common value," not a genuine distance-class relationship. Both documents were corrected rather than left as originally (and more impressively) worded.

### Investigated: why 153 catalog events have no matching circular

Checked directly rather than guessing. Ruled out a pipeline bug first (none of the sampled missing IDs appear anywhere in the raw archive text at all - not an extraction failure). Ruled out a stale archive next (the "missing" rate is scattered proportionally across every month back to 2019, not concentrated in recent months - a stale snapshot would only affect the newest months). The real explanation: **median FAR for matched events is 1×10⁻⁵/yr (highly significant); median FAR for missing events is 3/yr (essentially noise-level)**. These are low-significance candidates that made it into the offline/retrospective catalog release but never triggered a real-time public GCN alert during the observing run - so no circular was ever written for them. A real, well-evidenced reporting gap, not a defect in this project's pipeline.

### Write-up done

The catalog-validation finding, the missing-events investigation, and the corrected baseline explanation are now written into `feasibility_draft.md` (new Section 6, renumbered subsequent sections) and the LaTeX thesis (`04_results_and_discussion.tex` new section, `05_conclusion.tex` Summary/Limitations/Future Work updated, `01_introduction.tex` objectives updated, `frontmatter/abstract.tex` updated) — not left as a chat-only result.

### Remaining / in progress

- Day 2's originally planned M5.1 (source-class breakdown) and M4.4 (extraction gold-sample) are still pending, deprioritized in favor of the catalog work once it turned out to be immediately productive.

### For the supervisor

- Still no response on the feasibility memo's open questions. Proceeding with the GWTC catalog integration on the user's own authorization in the meantime, explicitly revisable if the supervisor raises concerns later.

---

## 2026-08-20 (Day 1 of the sprint)

### What we did

- Added MAE, RMSE, and bias to the validation metrics (M7.3).
- Added two trivial baselines — source-class midpoint and population-average (M7.5).
- Wrote `project_inventory.md` and `code_audit.md` (M1); in the process found the two governing planning documents only existed as pasted chat content and saved them into `docs/`.
- Checked the environment for the later Pathfinder build: confirmed a venv works around the blocked direct `pip install`, confirmed no LLM API key is configured.
- Restructured the repo into `shared/` (pipeline code used by both the estimator and the future Pathfinder) plus `legs/{leg1_estimation,leg2_ai_comparison,leg3_pathfinder}/`, one folder per thesis leg. Both entry points re-verified to produce identical output after the move.
- Added a dated changelog to `README.md` and corrected stale, unverified event-count claims it had carried over from before this week's bug fixes.
- Set up a LaTeX thesis skeleton (`thesis/latex/`) matching the Tribhuwan University project-work template structure, with real research content already written into the Introduction/Methods/Results/Conclusion chapters.
- Deleted the stale pre-fix CSV output (`.\o4a_gw_dataset.csv`) and saved the five reference PDFs' content as notes under `docs/references/`, since only their extracted text was available, not the original files.
- Two commits made and pushed to `origin/main`.

### Challenges / surprises

- **The class-midpoint baseline turned out to be competitive with the statistical estimator** — beating it on the ±25%-error metric and tying it on bin-hit rate, despite doing zero fitting. This wasn't expected going in, and required walking back how confidently the draft could claim the statistical model was "learning something from distance" versus mostly reflecting the same signal source classification already carries.
- **Properly calibrating the physics formula's constant C didn't rescue it.** Fitting C via leave-one-out cut the error substantially, but a systematic bias with distance (r=0.55) survived calibration entirely — direct evidence the formula's problem is structural (a genuinely missing input, network SNR) rather than a badly chosen constant.
- **No LaTeX compiler is available in this environment**, so the new thesis skeleton could not be test-compiled here. It needs to be opened on Overleaf (or compiled locally) to confirm it actually builds before relying on it.
- **GitHub push has no persistent credential path set up** (by design — nothing is left on disk between sessions), so each push has needed a fresh token from you. Not a blocker, just a recurring small friction worth knowing about.
- Restructuring into `shared/`/`legs/` broke both entry-point scripts' invocation (`python3 run_pipeline.py` no longer resolves the packages) until switched to module invocation (`python3 -m legs.leg1_estimation.run_pipeline`) — caught immediately by re-running both scripts after the move, not a lingering issue, but worth remembering if new entry points get added later.

### Remaining / carried into Day 2+

- LaTeX front-matter institutional details (university, supervisor, degree title, roll number, etc.) — waiting on the sample project you'll share to pull them from.
- LLM API key — you're providing this for Day 2, needed before the Day 8-9 Pathfinder prototype work.
- Day 2 sprint tasks: M7.4 required plots, M5.1 availability breakdown by source-class, M4.4 gold-sample preparation.

### For the supervisor

- Still no response on the feasibility memo's open questions (whether 10-25% error is a hard requirement, whether an external catalog like GWTC/GWOSC is an acceptable scope addition, whether a documented negative/limited result is an acceptable thesis outcome) — these remain open and increasingly relevant as more evidence (the calibration finding, the baseline finding) accumulates in the same direction.
