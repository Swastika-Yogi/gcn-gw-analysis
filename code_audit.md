# Code Audit

> Deliverable for Master Plan M1.2. Every file below has actually been run at least once, not just read.

## Entry points

### `run_pipeline.py`
- **Purpose:** Download/cache circulars, filter to GW-related, group by event within the O4a window, parse fields, print a data-availability report, save `data/processed/o4a_event_table.csv`.
- **Inputs:** none (downloads from `https://gcn.nasa.gov/circulars/archive.json.tar.gz` if `./jsons/archive.json` doesn't already exist).
- **Outputs:** `data/processed/o4a_event_table.csv`, stdout report.
- **Packages:** `requests` (stdlib otherwise).
- **Hard-coded paths:** `./jsons`, `data/processed/o4a_event_table.csv` — both relative to repo root, no credentials.
- **Status:** `WORKING`. Run repeatedly this session; last run: 181 O4a events, 89%/46%/45%/0% field coverage.

### `validate_estimator.py`
- **Purpose:** Build the all-runs event table, construct the 49-event validation set (self-reported reference mass, non-Terrestrial), run all four estimators/baselines via leave-one-out, print comparison, save `data/processed/validation_results.csv`.
- **Inputs:** none (same download/cache as above).
- **Outputs:** `data/processed/validation_results.csv`, stdout report.
- **Packages:** stdlib only (`csv`, `math`).
- **Status:** `WORKING`. Last run confirmed all four rows (physics uncalibrated / physics calibrated / statistical / two baselines) print and the CSV writes correctly.

## `src/ingestion/`

### `load_gcn_archive.py`
- **Purpose:** `download_and_extract()` (skips download if `./jsons/archive.json` exists), `load_circulars()` (reads every JSON file, skips malformed ones silently), `circular_text()` helper.
- **External API:** `gcn.nasa.gov` — public, no auth.
- **Status:** `WORKING`.

## `src/parsing/`

All five parser modules take raw circular text and return a list of candidate matches with `confidence` and `source_text` for provenance. None have external dependencies or hard-coded paths.

- `event_id_parser.py` — `WORKING`. **Bug found and fixed 2026-08-19:** original regex `S\d{6}[a-z]\b` only matched single-letter suffixes; real IDs go to 2-3 letters on busy days (e.g. `S250629ae`). Fix: `[a-z]{1,3}`.
- `mass_parser.py` — `WORKING`. Two extraction paths: high-confidence bin sentence, low-confidence generic "mass" keyword proximity (the latter is noisy by design, documented in its own docstring).
- `distance_parser.py` — `WORKING`.
- `far_parser.py` — `WORKING`.
- `classification_parser.py` — `WORKING`. **Bug found and fixed 2026-08-19:** regex only handled `(<1%)`, not `(>99%)`, silently dropping `p_bbh` and mislabeling `source_class` for high-confidence detections (the common case).
- `snr_parser.py` — `WORKING` as a deliberate no-op. Checked: "SNR" in circular text is almost always an unrelated instrument's own follow-up SNR, not the LVK network SNR — confirmed by direct inspection of ~8 sample matches.

## `src/processing/`

- `group_by_event.py` — `WORKING`. `RUN_WINDOWS` currently only defines `"O4a": (230524, 240116)`; add more named windows here if other runs get pulled in.
- `build_event_table.py` — `WORKING`. Resolves multiple circulars per event by highest-confidence extraction per field (`CONFIDENCE_RANK`); logs every kept value to a provenance list.

## `src/modeling/`

- `chirp_mass_estimator.py` — `WORKING`. Implements `M_z = C * (rho*D_L/F(iota))^1.2`. `mass_frame` param currently only accepts `"detector"` — will raise `ValueError` otherwise (deliberate, not a bug).
- `statistical_estimator.py` — `WORKING`. Hand-rolled OLS (Gaussian elimination) since numpy isn't installed in this environment — confirmed via `import numpy` failing on 2026-08-19.
- `apply_estimator.py` — `WORKING`. Holds the assumed constants (`ASSUMED_SNR=15`, `ASSUMED_COS_IOTA=0.5`, `ASSUMED_C=1e-4`) used by the uncalibrated physics baseline.
- `calibration.py` — `WORKING`. Added 2026-08-20 for M6.2.
- `baselines.py` — `WORKING`. Added 2026-08-20 for M7.5.

## `src/validation/`

- `build_validation_set.py` — `WORKING`.
- `metrics.py` — `WORKING`. `summarize()` extended 2026-08-20 to add MAE/RMSE/bias.

## `src/analysis/`

- `reports.py` — `WORKING`.

## Environment notes (checked 2026-08-20, de-risking Days 8-10)

- **numpy/matplotlib/sentence-transformers/scikit-learn: none installed.** All regression/least-squares code in this repo is hand-rolled specifically to avoid this.
- **`pip install` is blocked directly** (Debian's externally-managed-environment / PEP 668 protection).
- **Fix confirmed working:** `python3 -m venv --system-site-packages .venv` + installing via that venv's pip. Tested live with numpy 2.5.2 - succeeds. Use this for any Day 2+ (plots) or Day 8-10 (embeddings) package needs.
- **Internet access: confirmed** (`gcn.nasa.gov` and `pypi.org` both reachable).
- **No LLM API key found in this environment** (checked `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and a general grep for `api_key`/`anthropic`/`openai` in env vars - none present). **This blocks Day 9's "LLM answers from retrieved context" step as currently scoped** - either a key needs to be supplied, or that step gets scoped down to retrieval + structured/templated answers without live generation. Flagged for a decision before Day 8.

## Deleted / historical

- `gcn_analysis.py` — deleted 2026-08-19 (git commit `cec586b3`), fully superseded by the `src/` layout. Its output file `./o4a_gw_dataset.csv` is still sitting in the repo root — see `project_inventory.md`, flagged `needs_review`.
