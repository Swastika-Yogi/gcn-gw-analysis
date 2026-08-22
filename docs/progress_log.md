# Progress Log

Detailed daily record, separate from `README.md`'s terse one-line-per-change changelog. Each entry: what got done, what was harder than expected or genuinely surprising, what's still open, and anything worth raising with the supervisor. Written at the end of each working day.

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
