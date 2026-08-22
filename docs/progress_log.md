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

### Revisited the FAR→SNR proxy — reversed an earlier conclusion, with a caveat

The earlier "FAR is a weak proxy" finding (r ≈ −0.34) used a back-solved, noisy stand-in for SNR on only 49 events. Testing directly against 381 real (SNR, FAR) catalog pairs instead gives r = −0.70 and 10.7% median SNR-prediction error — a real, usable relationship. Didn't stop at the headline number, though: binning by FAR magnitude shows the proxy is *least* accurate for the most significant events (19.7% median error, likely because pipelines floor their reported FAR, collapsing many true SNRs onto one value) and *most* accurate for marginal events (5.6%). Applying the proxy downstream to the 49-event circular-only set gave only a modest gain (44.8% → 39.5% median chirp-mass error) — smaller than the headline proxy number would suggest, but the reason is traceable: those 49 events sit in the harder FAR range (median 4.1×10⁻³/yr), and none of them are in the catalog yet to check directly. Corrected the earlier "weak proxy" claim in both `feasibility_draft.md` and the LaTeX thesis rather than leaving it stand.

### Revisited the combined class+distance model — this time with a clean answer

Explicitly rejected earlier (2026-08-22, above) for lack of class diversity in the 49-event circular-only set (48/49 BBH). The 214-event catalog-backed set has real diversity (206 BBH, 5 NSBH, 2 Terrestrial, 1 BNS) — still too thin for per-class dummies, so used a single binary BBH-vs-not predictor instead, stated as a limitation rather than hidden. On the 212 non-Terrestrial events: distance alone = 27.8% median error, class alone = 38.5%, combined = 28.9% (no better than distance alone, arguably marginally worse). Clean result this time: class doesn't add signal beyond distance. Unplanned bonus finding: distance-only at this scale (27.8%) is now competitive with the physics formula's real-SNR result (31.5%) — the simplest circular-derivable model matches a physically-motivated one that needs information circulars can't supply. Written into `feasibility_draft.md` (new subsection in Section 6, updated Discussion/Decision-Gate) and the LaTeX thesis (`04_results_and_discussion.tex` new subsection + two updated passages, `05_conclusion.tex` Summary/Future Work updated).

### M5.1 — full availability breakdown, and a sharper version of an earlier finding

Went back to finish the two Day 2 tasks deprioritized earlier (below). `RUN_WINDOWS` only had O4a defined; added real O3a/O3b/O4b/O4c date windows (looked up LVK's actual observing-run schedule) so the archive's 505 S-ID events could be broken down by run, not just "O4a vs everything else." Built `legs/leg1_estimation/analysis/availability_analysis.py` covering: coverage by run, by source class, by circular type (identification/update/retraction/external-followup/other, classified from the subject line), and typical reported uncertainty.

The headline finding sharpens something already written up rather than being new: the reference-chirp-mass bin sentence isn't merely "rare" outside O4c (10.1% overall, as previously stated) — it's **completely absent from every event before O4c** (0/400 across O3a–O4b) and present in the majority of O4c events (51/87, 58.6%). This means the circular-only validation set used throughout Sections 5–8 is drawn from a single recent run by construction, not by chance of which events happened to report the field — worth stating plainly rather than leaving as an implicit fact buried in a percentage. Also confirmed numerically why every validation set built so far skews BBH: 285/313 classified events (91%) are BBH, archive-wide — a real population fact, not a sampling artifact of this pipeline.

### M4.4 — gold-sample audit, and a real bug found because of it

Built `legs/leg1_estimation/analysis/gold_sample_audit.py`: 30 circulars (general pool) + 15 more (O4c-only, since the chirp-mass field needs an O4c-specific sample to test at all) hand-annotated by reading the raw text directly, before looking at any parser output. All four parsers scored perfect precision/recall/F1 on this 45-circular sample — but the audit was worth doing regardless, because the *process* of hand-reading every circular surfaced a real, live bug that a clean scorecard would have hidden: `far_parser.py`'s regex accepted bare, case-insensitive "far" as the FAR abbreviation, with no word boundary against the ordinary English word. Confirmed directly: "So far, only 0.003 percent of the localization region has been covered" was silently parsed as FAR = 0.003 Hz. Fixed by requiring the bare abbreviation to be exact-case `FAR`; verified no regression on real archive coverage (317/505 events unchanged) while per-circular spurious noise dropped. Also caught, and left undisturbed rather than "fixed" (since there's nothing meaningful to fix): one circular where the archived "±" character is corrupted to a mojibake replacement character, silently losing a real uncertainty bound while keeping the correct central value; and two circulars misclassified by the (separate) M5.1 circular-type classifier because non-LVK authors conventionally open their subject line the same way LVK does.

### M5.2 / M5.3 — closing out Milestone 5

Quick synthesis rather than new analysis: M5.2's direct-vs-approximated table pulls together every availability finding so far into one place per-parameter (source, what needs it, what's used when it's missing, and a risk rating) — network SNR is the only "High" risk row, which is really just restating the project's central finding in table form. M5.3 turned up one genuinely new thing worth recording: sky-localization area ("90% credible region is X deg²") is present in 299/505 events (59.2%) and isn't extracted by this pipeline at all yet — comparable coverage to FAR/classification, flagged as a real future-work candidate rather than chased further this session, since it's new scope (a new parameter) rather than a chirp-mass refinement.

### M6.3 — run-specific calibration, and why the finer split doesn't fully win

Picked up Day 3 with the one M6.3 checklist item not yet tried: does calibrating the physics formula's C separately per observing run (rather than one global C) help, now that real per-run windows exist and the 214-event catalog-backed set has real per-event SNR? Built `validate_run_stratified_calibration.py`. Short answer: yes, but the interesting part is *how*. Per-run LOO calibration drops median error from 31.5% to 26.6% overall, but that's not uniform — it helps a lot on the two big runs (O4a, O4b, n=76/94) and actively hurts the two small ones (O3a, O3b, n=25/18), because refitting C via leave-one-out on <25 events is genuinely unstable. The fitted C values themselves cluster cleanly into two eras (~8.8e-5 for O3, ~5.9e-5 for O4, a real ~50% difference plausibly reflecting actual detector-network changes), so merging to era-level (O3 vs O4) instead of full per-run gives the same 26.6% median with more stable per-fold sample sizes — the version kept for write-up. Worth recording as a small methodological lesson: stratifying further isn't automatically better, and checking the fitted-parameter values directly (not just the aggregate error) is what caught it here.

### Remaining / in progress

- Milestone 5 (M5.1-M5.3) and M6.3 are now done.
- Remaining M6.3 items not attempted this session: orientation marginalization, network- (as opposed to run-) specific calibration.

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
