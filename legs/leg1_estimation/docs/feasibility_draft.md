# Chirp-Mass Estimation from GCN Circulars: Data Availability and Estimator Feasibility

*Draft section — adapt headings/numbering to match final thesis structure.*

## 1. Motivation

Full gravitational-wave parameter estimation for a compact-binary merger can take hours to days after the initial detection alert. In that window, electromagnetic follow-up teams must decide where to point telescopes using only the information published in GCN Circulars — short, public text bulletins issued by the LIGO/Virgo/KAGRA (LVK) collaboration and by follow-up observers. A fast, even approximate, chirp-mass estimate derived from circular text alone would let follow-up teams prioritize candidates (e.g. distinguishing likely binary neutron star mergers, which produce electromagnetic counterparts, from binary black hole mergers, which generally do not) before full parameter estimation is available.

This work asks two questions: (1) what physical information do GCN circulars actually contain, and (2) can that information support a chirp-mass estimate accurate enough to be useful.

## 2. Data and Pipeline

The dataset is the full public GCN circular archive (45,268 circulars at time of writing), downloaded via the GCN API. The processing pipeline (`src/`) performs, in order:

1. **Ingestion** — download and load all circulars as structured records (subject, body, circular ID, timestamp).
2. **GW filtering** — keyword screen (LIGO/Virgo/KAGRA mentions) to isolate GW-related circulars (3,624 of 45,268).
3. **Event identification** — regex extraction of LVK superevent IDs (`S<YYMMDD><letter-suffix>`). Note: the suffix grows from one letter to two once a day's single-letter allocation is exhausted; an ID regex restricted to one letter silently drops every event from a busy day. Correcting this nearly doubled the number of O4a events found in this study (79 → 181), which is itself a small methodological finding worth noting — under-inclusive ID matching is an easy, easy-to-miss source of sample bias in circular-based studies.
4. **Grouping** — circulars grouped by event, optionally restricted to a named observing-run date window.
5. **Field extraction, with provenance** — per-circular regex extraction of luminosity distance, false alarm rate (FAR), source classification probabilities (BBH/BNS/NSBH/Terrestrial), and, where present, chirp mass. Each extracted value is logged with its source circular ID and source text for traceability.
6. **Event table construction** — one row per event, taking the highest-confidence extraction per field across all circulars mentioning that event.

## 3. Data Availability

Restricting to the O4a observing run (2023-05-24 to 2024-01-16) as a case study, 181 events were identified. Field coverage:

| Field | Coverage | Notes |
|---|---|---|
| Luminosity distance | 161/181 (89%) | 3–6,653 Mpc; only 82 events include an explicit ± uncertainty |
| False alarm rate | 83/181 (46%) | Spans 1.1×10⁻⁵⁰ to 3.2×10⁻⁵ Hz |
| Source classification | 81/181 (45%) | 79 BBH, 2 NSBH, no confident BNS in this set |
| Network SNR | 0/181 (0%) | "SNR" appears in circulars, but almost always as an unrelated instrument's own follow-up SNR (X-ray/optical), never the LVK trigger's network SNR |
| Orbital inclination | 0/181 (0%) | Not reported in any circular checked |
| Reference chirp mass | 0/181 (0%) | The bin-probability sentence LVK circulars use for chirp mass (Section 4) does not appear in any O4a-era circular; it appears only in later-run circulars |

This is itself a finding: two of the three quantities the standard SNR-scaling relation (Section 4) requires — network SNR and inclination — are structurally absent from circular text, not merely difficult to parse.

### 3.1 Comparison: O4a only vs. the full archive (all observing runs)

The table above restricts to O4a as a case study. Repeating the same check across every event in the archive, all runs combined, gives a fuller picture:

| Field | O4a only (181 events) | All runs (505 events) |
|---|---|---|
| Luminosity distance | 89.0% | 83.6% |
| False alarm rate | 45.9% | 62.8% |
| Source classification | 44.8% | 62.0% |
| Reference chirp mass | 0.0% | 10.1% (51 events) |
| Complete case (distance + FAR) | 45.3% | 62.4% |

Coverage is meaningfully *better* once later runs are included, not worse — FAR and classification both improve by roughly 17 percentage points, and distance coverage only dips slightly. The most likely explanation is that LVK's circular-writing template became more complete and standardized over time, so later-run circulars report more fields consistently than O4a-era ones did — itself a small additional finding: data quality here is improving as the observing program matures, not staying flat. The reference-chirp-mass figure (51 events, 10.1%) is the same population that makes up the validation set in Section 5.

## 4. Two Estimators

### 4.1 Physics-based (SNR-scaling) estimator

Following the standard inspiral SNR expression, chirp mass can be written as

M_z = C · (ρ · D_L / F(ι))^(6/5)

where ρ is network SNR, D_L is luminosity distance, F(ι) is an orientation factor bounded in [0.5, 1.0], and C absorbs detector-noise and unit-conversion terms. Since ρ and ι are unavailable per-event, this study used fixed assumed values (ρ = 15, cos ι = 0.5, C = 1×10⁻⁴) representative of a confident detection.

### 4.2 Statistical (empirical) estimator

As an alternative that avoids assuming SNR, chirp mass was instead modeled as a log-linear function of fields that *are* present in circulars:

log M = a + b · log D_L

fit by ordinary least squares against events with a self-reported reference chirp mass (Section 5). This is a population-level statistical relationship — plausibly reflecting a real detection-selection effect (heavier, louder binaries are detectable to greater distances) — not a per-event physical derivation, and is reported as such.

## 5. Validation Set

O4a-era circulars report no reference chirp mass at all, so validation used the full archive (all observing runs). 49 events report a chirp-mass bin directly (via the sentence "the source chirp mass falls with highest probability in the bin (X, Y) solar masses"), together with distance and a non-Terrestrial classification. Note that this reference value is itself coarse: LVK's low-latency pipeline reports mass as one of a small number of roughly factor-of-2-wide bins, not a continuous measurement — so even a "perfect" estimator cannot be expected to beat the bin's own width.

## 6. Validation Against the Real GWTC Catalog

Section 5's validation set is limited by what circulars self-report: 49 events, entirely BBH bar one, and — critically — no event has a real network SNR, since that quantity is structurally absent from circular text (Section 3). The public GWTC catalog (via the GWOSC API) removes that limitation: it publishes real, measured chirp mass and real network SNR for every confirmed event.

**ID cross-matching.** GWTC event names (e.g. `GW230627_015337`) differ from circular superevent IDs (e.g. `S230627c`), but GWOSC's per-event `gracedb_id` field gives the exact circular ID directly for any event from 2019 onward (confirmed: `GW230627_015337`'s `gracedb_id` is `S230627c`, matching the circular event exactly). Pre-2019 events use an older `G`-prefixed GraceDB ID from before the superevent system existed and are out of scope for this cross-match.

**Coverage.** Of 380 confirmed post-2019 catalog events, 227 matched to at least one circular in our archive; 153 did not. This gap was checked directly rather than assumed benign: none of the missing IDs appear anywhere in the raw archive text (ruling out a parsing bug), and the missing rate is scattered proportionally across every month from 2019 to 2025 (ruling out a stale/incomplete archive snapshot — that would only affect the newest months). The actual explanation: median FAR for matched events is 1×10⁻⁵/yr (highly significant) versus 3/yr for missing events (essentially noise-level). The missing events are low-significance candidates added to the catalog through offline/retrospective analysis after the observing run, which never triggered a real-time public alert circular. This is a real, structural ceiling on any circular-based pipeline — roughly 40% of confirmed events in this period were never publicly announced via circular at all — independent of any extraction-completeness issue within the pipeline itself.

**Real-SNR validation.** Combining circular-extracted distance with catalog-provided real chirp mass and real SNR gives a 214-event set (4.4× the circular-only validation set), spanning a real mix of source classes rather than being almost entirely BBH. The physics formula (Section 4.1) was re-tested on this set two ways — with the real SNR, and with the same fixed assumed SNR = 15 used throughout Section 5 — using the identical leave-one-out C-fitting procedure (Section 4.4) in both cases, so the *only* thing that changes between the two runs is whether SNR is real or assumed:

| SNR source | Median % error | Within ±25% | MAE | Bias |
|---|---|---|---|---|
| Assumed (fixed at 15) | 46.6% | 58/214 (27%) | 14.46 M☉ | +5.79 M☉ |
| Real (catalog) | 31.5% | 89/214 (42%) | 9.18 M☉ | +2.88 M☉ |

Supplying the real SNR — with nothing else about the formula, the distance input, or the fitting procedure changed — cuts the median error by roughly a third and nearly doubles the within-±25% rate. This is a direct, controlled confirmation of the argument built up through Sections 3–7 from first principles and sensitivity analysis: SNR was the dominant error source, not a calibration problem or a flaw in the formula itself. The physics formula is not "wrong" in the abstract — it is specifically unusable *from circulars alone*, because circulars cannot supply the one input it depends on most.

Even with real SNR, 31.5% median error is still short of the 10–25% target for most events — real-world measurement uncertainty, the fixed orientation assumption (cos ι = 0.5, never marginalized or measured), and unmodeled detector/pipeline effects absorbed into a single global C all remain. But the gap closed by switching from assumed to real SNR is the largest single improvement found anywhere in this investigation, larger than calibration (Section 7, circular-only) achieved on its own.

## 7. Results (Circular-Only Validation)

Leave-one-out cross-validation on the 49-event circular-self-reported set, comparing predicted chirp mass to the reference bin midpoint:

| Estimator | Median % error | Within ±25% | Correct bin |
|---|---|---|---|
| Physics, C fixed at methodology note's value (1×10⁻⁴) | 115% | 5/49 (10%) | 7/49 (14%) |
| Physics, C properly fit per fold (no leakage) | 45% | 13/49 (27%) | 20/49 (41%) |
| Statistical (distance only) | 33% | 17/49 (35%) | 25/49 (51%) |
| Baseline: source-class midpoint (no fitting at all) | 50% | 23/49 (47%) | 23/49 (47%) |
| Baseline: population average (LOO) | 50% | 0/49 (0%) | 23/49 (47%) |

Adding FAR or BBH-classification probability as additional regression predictors did not improve the statistical model (median error rose to 36–41%) — with only 49 samples, extra predictors overfit rather than add signal, and BBH probability has little variance across the sample (mostly 96–99%).

**On the calibration constant C.** The original C = 1×10⁻⁴ came from the methodology note's single worked example, not a fit against data — using it as-is is an assumption, not a calibration. Fitting C properly (closed-form, since SNR and orientation are held fixed so C is the formula's only free parameter; leave-one-out to avoid any leakage between calibration and validation events) gives a fitted C of ≈5.6×10⁻⁵ — about 1.8× smaller than the methodology note's value — and cuts the physics formula's median error from 115% to 45%. The fitted C is stable across folds (5.44×10⁻⁵ to 5.78×10⁻⁵ across all 49 leave-one-out refits), so instability in C is not the limiting factor.

**A trivial baseline is competitive with the statistical model — but not for the reason first assumed.** Guessing a fixed typical mass for an event's classified source type — no distance, no fitting, no per-event information at all — gets a 47% within-±25% rate and a 47% bin-hit rate, both close to (and on the ±25% metric, better than) the distance-only statistical model's 35%/51%. The initial explanation for this (that distance and source class are correlated, since heavier BBH systems are both louder and visible further out) does not hold up: the 49-event validation set is 48/49 (98%) BBH, with only one unclassified event and zero BNS/NSBH. There is essentially no class diversity in this sample to correlate distance against. The baseline's competitiveness more plausibly reflects that guessing near the sample's dominant, modal value is a strong strategy when the sample is this concentrated in one class — not evidence of a genuine distance-class relationship. (The population-average baseline, by contrast, is uniformly bad — 0% within ±25% — confirming per-event structure of *some* kind is genuinely needed, even if this sample can't establish what kind.)

**What calibration cannot fix.** Even with a properly fit C, the physics formula's log-residuals correlate with log-distance at r = 0.55 — a substantial systematic bias. This is expected: C is a single global constant, but the quantity it's standing in for a fixed, uniform SNR assumption is intrinsically distance-dependent in reality (true SNR falls off with distance; this model holds it fixed). No choice of C, however well fit, can absorb a bias that varies systematically with an input the model treats as constant. This is the clearest evidence that the physics formula's shortfall is structural — the missing per-event SNR — not a calibration problem.

**Figures** (generated by `legs/leg1_estimation/generate_plots.py`, saved in `legs/leg1_estimation/figures/`): for each estimator, an estimated-vs-reference scatter plot with a y=x reference line, a residual-vs-predicted plot, an error histogram, and error-vs-distance. The error-vs-distance plots are the most direct visual confirmation of the bias argument above — `physics_uncalibrated_vs_distance.png` shows error rising sharply and consistently with distance (up to ~700%), and `physics_calibrated_vs_distance.png` shows the same rising trend at a compressed scale (up to ~400%) after calibration — visually, not just numerically, showing that calibration shrinks the problem without removing its distance-dependent shape. `statistical_scatter.png` shows the discrete vertical banding from the bin-quantized reference values (masses cluster at 8.25/16.5/33/66 M☉, the bin midpoints) rather than a continuous spread — a visual reminder of the coarse-ground-truth point made throughout this section.

## 8. Discussion

**The physics formula is dominated by an unrecoverable input.** M scales as ρ^1.2, so a factor-of-2 error in assumed SNR produces roughly +130%/−56% error in the mass estimate. Reproducing a mass error within 10–25% requires ρ known to within roughly ±20%; real network SNRs for confident O4a-era detections plausibly span ~8 to 30+, far wider than that tolerance. Holding SNR fixed while distance varies over three orders of magnitude means the physics estimator effectively tracks distance, not mass. This is not a calibration artifact: properly fitting C halves the median error (115% → 45%) but leaves a strong residual bias correlated with distance (r = 0.55, Section 7) — exactly what this sensitivity argument predicts, since C cannot absorb an input the model treats as constant when it physically isn't. Section 6's catalog validation confirms this directly rather than just by argument: giving the same formula real SNR instead of an assumed one, with nothing else changed, cuts median error from 46.6% to 31.5%.

**FAR is a weak, insufficient proxy for SNR.** The SNR value that would make the physics formula match each event's true reference mass ("required ρ") correlates with log(FAR) at only r ≈ −0.34 across the validation set — some relationship exists, as expected physically, but far too weak to substitute for a real SNR measurement, and confirmed empirically by FAR's failure to improve the regression model.

**The statistical model performs better, but is a different kind of result.** It captures real, exploitable structure (a selection effect between detection distance and mass) rather than a physical single-event inference. A median error of 33% and a 51% correct-bin rate is a meaningfully useful signal — enough to substantially narrow the plausible mass range for a new event before parameter estimation completes — but does not meet a strict 10–25% accuracy target for a majority of events.

### Decision-gate classification

Per the project plan's M6 decision gate (`validated_approximation | useful_constraint | exploratory_only | unsupported`):

- **Physics (SNR-scaling) estimator, circular-only inputs: `unsupported`.** Fails even after properly fitting its calibration constant, with a systematic, physically-explained bias that no calibration choice can remove — because the one input it depends on most (SNR) is structurally absent from circular text. Section 6's catalog validation clarifies the scope of this: the formula itself is not unsupported in the abstract (given real SNR, it more than halves its own error), only as a circular-derived estimator specifically.
- **Statistical (distance-only) estimator: `useful_constraint`.** Not a validated per-event measurement, but a real, reproducible signal (best MAE and bin-hit rate of any method tested) useful for narrowing the plausible mass range. Caveat: a source-class-midpoint baseline with zero fitting is competitive on several metrics (Section 7), so this label credits "distance plus whatever it correlates with," not distance as an independently powerful signal in its own right.

## 9. Limitations

- The circular-only validation set is small (n = 49); leave-one-out cross-validation was used to reduce (not eliminate) overfitting risk given the sample size. The catalog-backed set (Section 6, n = 214) is substantially larger but has its own known limitation: 153 confirmed events are structurally excluded, since low-significance offline catalog additions were never announced via public circular (Section 6).
- Circular-self-reported reference-mass events are, by construction, drawn from later observing runs than O4a, since O4a circulars never report this field. O4a data was used for the availability audit and can be scored by the fitted model, but contributed no circular-only validation examples (the catalog-backed validation set does include O4a events, since the catalog itself has no such reporting gap).
- The regression uses only distance; other circular-derivable fields (FAR, classification) were tested and did not help at this sample size, but may with a larger dataset as the archive grows.
- No independent held-out test set beyond leave-one-out; results should be revisited as more circulars with reference chirp mass accumulate, and as the catalog itself grows.
- Even with real SNR, the physics formula still uses a fixed orientation assumption (cos ι = 0.5, never marginalized or measured) and a single global calibration constant absorbing all detector/pipeline effects — both untested as further error sources.

## 10. Open Questions

- Is a 10–25% error target a hard requirement, or a starting point that this data can reasonably revise? (Now more pressing: even with real SNR from the catalog, median error is 31.5%, still outside that band for most events.)
- ~~Would incorporating an external reference catalog (e.g. GWTC/GWOSC) for calibration be an acceptable scope expansion~~ — **resolved**: done (Section 6), on the user's own authorization, pending supervisor sign-off.
- Given the coarse, bin-based nature of the circular-reported ground truth, should "predict the correct bin" replace "predict within X% error" as the primary success metric? (Less relevant for the catalog-backed set, whose reference values are continuous, not binned.)
- Should the thesis report circular-only results as the honest headline finding (matching the original circular-only research question) and catalog-backed results as a supplementary robustness check — or the reverse?

## Reproducibility

- Pipeline: `run_pipeline.py` (event table construction) → `data/processed/o4a_event_table.csv`
- Circular-only validation: `validate_estimator.py` → `data/processed/validation_results.csv`
- Catalog-backed validation: `validate_against_catalog.py` → `data/processed/catalog_validation_results.csv` (needs network access to `gwosc.org`; caches results in `data/raw/gwtc_catalog*.json` after first run)
- Plots: `generate_plots.py` (needs `../../.venv` + matplotlib, see repo root `requirements.txt`)
- Source: `shared/{ingestion,parsing,processing}/`, `legs/leg1_estimation/{modeling,validation,analysis}/`
