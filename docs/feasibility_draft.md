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

## 6. Results

Leave-one-out cross-validation on the 49-event set, comparing predicted chirp mass to the reference bin midpoint:

| Estimator | Median % error | Within ±25% | Correct bin |
|---|---|---|---|
| Physics, C fixed at methodology note's value (1×10⁻⁴) | 115% | 5/49 (10%) | 7/49 (14%) |
| Physics, C properly fit per fold (no leakage) | 45% | 13/49 (27%) | 20/49 (41%) |
| Statistical (distance only) | 33% | 17/49 (35%) | 25/49 (51%) |
| Baseline: source-class midpoint (no fitting at all) | 50% | 23/49 (47%) | 23/49 (47%) |
| Baseline: population average (LOO) | 50% | 0/49 (0%) | 23/49 (47%) |

Adding FAR or BBH-classification probability as additional regression predictors did not improve the statistical model (median error rose to 36–41%) — with only 49 samples, extra predictors overfit rather than add signal, and BBH probability has little variance across the sample (mostly 96–99%).

**On the calibration constant C.** The original C = 1×10⁻⁴ came from the methodology note's single worked example, not a fit against data — using it as-is is an assumption, not a calibration. Fitting C properly (closed-form, since SNR and orientation are held fixed so C is the formula's only free parameter; leave-one-out to avoid any leakage between calibration and validation events) gives a fitted C of ≈5.6×10⁻⁵ — about 1.8× smaller than the methodology note's value — and cuts the physics formula's median error from 115% to 45%. The fitted C is stable across folds (5.44×10⁻⁵ to 5.78×10⁻⁵ across all 49 leave-one-out refits), so instability in C is not the limiting factor.

**A trivial baseline is competitive with the statistical model.** Guessing a fixed typical mass for an event's classified source type — no distance, no fitting, no per-event information at all — gets a 47% within-±25% rate and a 47% bin-hit rate, both close to (and on the ±25% metric, better than) the distance-only statistical model's 35%/51%. This is worth stating plainly: since heavier BBH systems are both louder and visible further out, distance and source class are correlated, so the statistical model's apparent skill substantially overlaps with what source classification alone already tells you. The distance regression is not clearly adding much beyond what a well-informed guess by class already provides. (The population-average baseline, by contrast, is uniformly bad — 0% within ±25% — confirming per-event structure of *some* kind, whether from class or distance, is genuinely needed.)

**What calibration cannot fix.** Even with a properly fit C, the physics formula's log-residuals correlate with log-distance at r = 0.55 — a substantial systematic bias. This is expected: C is a single global constant, but the quantity it's standing in for a fixed, uniform SNR assumption is intrinsically distance-dependent in reality (true SNR falls off with distance; this model holds it fixed). No choice of C, however well fit, can absorb a bias that varies systematically with an input the model treats as constant. This is the clearest evidence that the physics formula's shortfall is structural — the missing per-event SNR — not a calibration problem.

## 7. Discussion

**The physics formula is dominated by an unrecoverable input.** M scales as ρ^1.2, so a factor-of-2 error in assumed SNR produces roughly +130%/−56% error in the mass estimate. Reproducing a mass error within 10–25% requires ρ known to within roughly ±20%; real network SNRs for confident O4a-era detections plausibly span ~8 to 30+, far wider than that tolerance. Holding SNR fixed while distance varies over three orders of magnitude means the physics estimator effectively tracks distance, not mass. This is not a calibration artifact: properly fitting C halves the median error (115% → 45%) but leaves a strong residual bias correlated with distance (r = 0.55, Section 6) — exactly what this sensitivity argument predicts, since C cannot absorb an input the model treats as constant when it physically isn't.

**FAR is a weak, insufficient proxy for SNR.** The SNR value that would make the physics formula match each event's true reference mass ("required ρ") correlates with log(FAR) at only r ≈ −0.34 across the validation set — some relationship exists, as expected physically, but far too weak to substitute for a real SNR measurement, and confirmed empirically by FAR's failure to improve the regression model.

**The statistical model performs better, but is a different kind of result.** It captures real, exploitable structure (a selection effect between detection distance and mass) rather than a physical single-event inference. A median error of 33% and a 51% correct-bin rate is a meaningfully useful signal — enough to substantially narrow the plausible mass range for a new event before parameter estimation completes — but does not meet a strict 10–25% accuracy target for a majority of events.

### Decision-gate classification

Per the project plan's M6 decision gate (`validated_approximation | useful_constraint | exploratory_only | unsupported`):

- **Physics (SNR-scaling) estimator: `unsupported`.** Fails even after properly fitting its calibration constant, with a systematic, physically-explained bias that no calibration choice can remove.
- **Statistical (distance-only) estimator: `useful_constraint`.** Not a validated per-event measurement, but a real, reproducible signal (best MAE and bin-hit rate of any method tested) useful for narrowing the plausible mass range. Caveat: a source-class-midpoint baseline with zero fitting is competitive on several metrics (Section 6), so this label credits "distance plus whatever it correlates with (largely source class)," not distance as an independently powerful signal.

## 8. Limitations

- Validation set is small (n = 49); leave-one-out cross-validation was used to reduce (not eliminate) overfitting risk given the sample size.
- Reference-mass events are, by construction, drawn from later observing runs than O4a, since O4a circulars never report this field. O4a data was used for the availability audit and can be scored by the fitted model, but contributed no validation examples.
- The regression uses only distance; other circular-derivable fields (FAR, classification) were tested and did not help at this sample size, but may with a larger dataset as the archive grows.
- No independent held-out test set beyond leave-one-out; results should be revisited as more circulars with reference chirp mass accumulate.

## 9. Open Questions

- Is a 10–25% error target a hard requirement, or a starting point that this data can reasonably revise?
- Would incorporating an external reference catalog (e.g. GWTC/GWOSC) for calibration be an acceptable scope expansion, given circulars alone cap the validation set at 49 events?
- Given the coarse, bin-based nature of the ground truth itself, should "predict the correct bin" replace "predict within X% error" as the primary success metric?

## Reproducibility

- Pipeline: `run_pipeline.py` (event table construction) → `data/processed/o4a_event_table.csv`
- Validation: `validate_estimator.py` (estimator comparison) → `data/processed/validation_results.csv`
- Source: `src/{ingestion,parsing,processing,modeling,validation,analysis}/`
