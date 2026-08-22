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

### 2.1 Extraction accuracy: a manual gold-sample audit (M4.4)

The parsers above were checked against manually annotated ground truth, not just assumed correct. `legs/leg1_estimation/analysis/gold_sample_audit.py` holds two fixed, seeded samples, each hand-annotated by reading the raw circular text directly (recording what's actually there *before* looking at parser output):

- A 30-circular general sample, drawn from the identification+update pool (the two circular types that carry almost all real field content — Section 3.2), covering distance/FAR/classification.
- A 15-circular O4c-only sample, since the reference-chirp-mass bin sentence doesn't exist before O4c (Section 3.2) — the general sample alone would have zero true positives for this field, too few to estimate anything from.

| Field | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| Distance | 27 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 |
| FAR | 17 | 0 | 0 | 13 | 1.00 | 1.00 | 1.00 |
| Classification | 17 | 0 | 0 | 13 | 1.00 | 1.00 | 1.00 |
| Chirp mass (O4c sample) | 12 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 |

All four parsers score perfectly on both presence/absence and, for every true positive, the extracted *value* against the hand-read value. This isn't a claim that the parsers are flawless in general — it's a claim about this specific 45-circular audit — but the audit process itself was worth doing regardless of the clean scorecard, because it surfaced two real issues that a scorecard alone would have hidden:

**A real bug, found and fixed.** `far_parser.py`'s regex treated bare, case-insensitive "far" as a reliable stand-in for the "FAR" abbreviation, with no word boundary against the ordinary English word. During annotation this was caught as a live false-positive risk, then confirmed directly: the sentence *"So far, only 0.003 percent of the localization region has been covered"* — nothing to do with false alarm rate — was silently parsed as FAR = 0.003 Hz. Fixed by requiring the bare abbreviation to appear as exact-case `FAR`, while keeping the full phrase "false alarm rate" case-insensitive (real circulars almost always spell it out; the bare abbreviation, when used, is written in caps). Verified this didn't regress real coverage — per-event FAR coverage on the full archive is unchanged (317/505 before and after) — while per-circular spurious matches dropped (Section 3.2's "lvk_other" and "external_followup" FAR columns: 13→9 and 4→3 respectively), confirming the fix removed noise rather than signal.

**A silent, low-impact information loss.** One sampled circular's archived text has its "±" character corrupted to a Unicode replacement character — an artifact of the archive itself, not this pipeline. The high-confidence "value ± error" regex correctly fails to match the corrupted symbol; the medium-confidence fallback still recovers the correct central value, but the real uncertainty bound is silently dropped, indistinguishable from an event that genuinely reported no uncertainty. Left as a documented limitation rather than special-cased, since detecting arbitrary encoding corruption is out of scope here.

**A boundary the M5.1 circular-type breakdown gets wrong, that field extraction doesn't.** Two of the 30 sampled circulars (an IceCube neutrino follow-up, a GROWTH galaxy cross-match) are not LVK-authored, but their subject lines conventionally open with `LIGO/Virgo <event-id>:` — the same convention LVK's own circulars use — so Section 3.2's subject-pattern circular-type classifier mislabels them as LVK "update"/"identification" circulars. This means that table's `external_followup` row is a slight undercount and `update`/`lvk_other` slight overcounts; a limitation of that specific classification heuristic, not of the four field-extraction parsers, which correctly extracted nothing field-wise from either (bar one genuine edge case, next).

**A genuine ambiguity, not a bug.** That same GROWTH circular reports a direction-conditioned posterior distance (`DISTMU = 272.35 Mpc`, evaluated at one external candidate's sky position) using the literal word "distance" — the parser's match is correct by its own definition, but this is a different quantity from the whole-sky-marginalized luminosity distance the LVK circulars themselves report. No fix applied; recorded as a known edge case a keyword-based parser can't be expected to distinguish.

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

### 3.2 Full breakdown: by run, source class, and circular type (M5.1)

`legs/leg1_estimation/analysis/availability_analysis.py` runs this breakdown directly from the archive (505 S-ID events, O3a through O4c; O1/O2 predate the `S`-prefixed superevent ID scheme and are out of scope for this ID-based grouping).

**By observing run:**

| Run | n | Distance | FAR | Classification | Chirp mass |
|---|---|---|---|---|---|
| O3a | 54 | 72.2% | 61.1% | 63.0% | 0.0% |
| O3b | 42 | 76.2% | 54.8% | 50.0% | 0.0% |
| O4a | 181 | 89.0% | 45.9% | 44.8% | 0.0% |
| O4b | 122 | 90.2% | 86.1% | 86.1% | 0.0% |
| O4c | 87 | 82.8% | 78.2% | 77.0% | 58.6% |

The reference-chirp-mass bin sentence is not merely rare in earlier runs — it is **completely absent from every run before O4c** (0/400 across O3a–O4b) and present in the majority of O4c events (51/87, 58.6%). This is a stronger and more specific finding than the earlier "10.1% overall" figure suggested: it means the entire circular-only validation set (Section 5) is drawn from a single, recent observing run by construction, not a coincidence of which events happened to report the field. FAR and classification both show the same O4b/O4c jump already noted above, now visible run-by-run rather than only "O4a vs. everything else."

**By source class** (among the 313 events with a classification):

| Class | n | Distance | FAR | Chirp mass |
|---|---|---|---|---|
| BBH | 285 | 100.0% | 99.6% | 16.8% |
| NSBH | 11 | 100.0% | 100.0% | 0.0% |
| BNS | 7 | 100.0% | 100.0% | 0.0% |
| Terrestrial | 10 | 90.0% | 100.0% | 20.0% |

BBH accounts for 285/313 (91%) of all classified events — this is the direct, quantified explanation for why every validation set built in this project so far has been overwhelmingly BBH (Sections 6 and 7): it reflects the real composition of the archive, not a sampling artifact of this pipeline.

**By circular type** (per-circular, not per-event — i.e. which *type* of circular actually carries each field):

| Type | n | Distance | FAR | Classification | Chirp mass |
|---|---|---|---|---|---|
| identification | 329 | 94.2% | 97.9% | 93.3% | 15.2% |
| update | 361 | 90.0% | 2.2% | 8.6% | 0.8% |
| retraction | 58 | 0.0% | 0.0% | 0.0% | 0.0% |
| external follow-up | 80 | 23.8% | 3.8% | 2.5% | 0.0% |
| lvk_other | 2,796 | 18.6% | 0.3% | 0.1% | 0.0% |

("identification" = the initial LVK alert circular, subject-matched on "Identification of a GW compact binary merger candidate"; "update" = any other LVK circular whose subject contains "update", e.g. revised sky localization or distance; "lvk_other" = LVK-issued circulars that are neither, e.g. non-detection or instrument-status notices; "external_followup" = circulars from other observatories reporting their own follow-up, which only mention the event ID.) FAR, classification, and chirp mass are almost entirely carried by the single initial identification circular — updates overwhelmingly revise distance/sky-location and rarely restate the others. This validates a modeling choice already built into the pipeline (`build_event_table.py` takes the highest-confidence value per field across all circulars for an event): for FAR/classification/mass, that is functionally equivalent to "read the identification circular," since almost nothing else supplies these fields. Retractions carry no field values at all, as expected for a withdrawn candidate.

**Typical uncertainty when reported:**

- Distance: 316/422 (74.9%) of distance-bearing events include an explicit ± bound; median relative half-width 29.2%.
- Chirp mass: all 51 reference values are bin midpoints with median relative half-bin-width 33.3% — a genuinely wide bin, not a tight measurement. This is useful context for the error percentages reported throughout Sections 6–7: a chirp-mass estimate landing within ±33% of the true value is roughly the same order as the uncertainty already built into the reference value itself.
- FAR and classification are reported as single point values / point probabilities in circular text, with no uncertainty given — marked not applicable rather than assigning a number that isn't actually there.

### 3.3 Direct vs. approximated quantities (M5.2)

Synthesizing the availability findings above against what each estimator actually needs:

| Parameter | Directly available | Source | Required for | Approximation if missing | Scientific risk |
|---|---|---|---|---|---|
| Luminosity distance | Sometimes (83.6%; 94.2% in identification circulars) | LVK identification/update circulars, whole-sky posterior mean ± std | Physics estimator, statistical estimator | None — event dropped (`no_distance` flag) | Low. Real posterior value with reported uncertainty (median 29.2% relative half-width) when present; risk concentrated only in the ~16% of events missing it entirely. |
| False alarm rate | Sometimes (62.8%) | Identification circular's online-analysis FAR | FAR→SNR proxy only | None — proxy unavailable for that event | Low–moderate. FAR itself is a real reported value; the derived SNR estimate carries its own error (10.7% median, worse for the most significant events, Section 6). |
| Source classification | Sometimes (62.0%) | Identification circular's classification probabilities | Class-midpoint baseline, combined class+distance model | None — combined model falls back to distance-only | Low. Section 6's result (class adds nothing beyond distance) means this gap costs nothing for the strongest current estimator. |
| Network SNR | Essentially never (0%) | Not directly available — "SNR" in circulars is almost always an unrelated instrument's own value | Physics estimator (dominant input) | (a) fixed assumed ρ=15 — high risk; (b) FAR→SNR proxy — 10.7% median error; (c) real value via GWTC catalog crosswalk — zero error but only for the 214 catalog-matched events, not new/unreleased ones | **High.** The single largest source of physics-estimator error found in this project (Section 6: real SNR alone cuts median error from 46.6% to 31.5%). |
| Orbital inclination | Never (0%) | Not directly available | Physics estimator's orientation factor F(ι) | Fixed cos ι = 0.5 throughout | Moderate but secondary. Bounded in [0.5, 1.0] by construction (caps its own maximum contribution, unlike SNR which is effectively unbounded); not yet tested empirically — flagged in Sections 9–10. |
| Reference chirp mass (bin) | Sometimes, structurally run-dependent (10.1% overall; 0% before O4c, 58.6% in O4c) | LVK identification circular's chirp-mass-bin sentence — itself coarse (median relative half-bin-width 33.3%), not a continuous measurement | Not an input — this is the *validation target* | GWTC catalog cross-matching (Section 6) supplies a real, continuous chirp mass for 214 events vs. 49 from circular self-report alone — already adopted as the practical answer | Low once catalog-matched; circular self-report alone would otherwise be a narrow, recent-run-only, quantization-limited ground truth. |

### 3.4 Additional discoveries (M5.3)

Findings noticed along the way that weren't part of the original plan, collected here rather than left scattered:

- **Correlations not originally planned.** Field coverage improves substantially between O4a and O4b/O4c (Section 3.2) — FAR and classification both jump from ~45% to ~78-86% — evidence LVK's circular-writing template became more complete over time, not that later events are intrinsically better-documented. Separately, the physics estimator's residual error correlates with distance even after calibration (r=0.55, Section 6/8) — the direct signature of a missing SNR term, since farther, quieter events are exactly where a fixed-SNR assumption breaks down hardest.
- **A useful parameter beyond chirp mass, not yet used.** Sky-localization area ("90% credible region is X deg²") appears in **299/505 events (59.2%)** — comparable coverage to FAR and classification, and not currently extracted by this pipeline. It's a plausible secondary parameter for future work: it correlates mechanically with distance and detector-network size, and would be directly useful for the GW Pathfinder leg (Section on Pathfinder) as a retrievable field electromagnetic follow-up teams actually query for.
- **Secondary scientific question worth naming.** Since localization area, distance, and network SNR are all connected through detector geometry, a natural follow-on question is whether SNR itself could be *partially* proxied from localization area the same way it was from FAR (Section 6) — not attempted here, but a concrete, testable extension.
- **Unexpected data-quality issues**, both already documented in the M4.4 audit above: an archive-side Unicode corruption of the "±" character that silently drops (not corrupts) reported uncertainty bounds; and inline post-publication correction notices (e.g. "[GCN OPS NOTE...]") embedded directly in body text, which didn't cause a parsing error in the events checked but are a latent risk for any future keyword-proximity parser added to this pipeline.
- **Decision on thesis inclusion.** The template-maturity and residual-distance-correlation findings are already written into Sections 3.2 and 8 respectively. The sky-localization-area coverage number is recorded here and flagged as future work (Section 10) rather than built out further this session, since it's a new parameter, not a refinement of chirp-mass estimation — in scope for a follow-on, not for the current estimator comparison.

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

**A FAR→SNR proxy revisited.** Section 8 (Discussion) reports an earlier test of whether FAR could substitute for SNR, finding only a weak correlation (r ≈ −0.34). That test used a *back-solved* "required ρ" from just 49 circular-only events — a noisy quantity that conflates the physics formula's own errors with any real FAR–SNR relationship. Testing the same idea directly against 381 real (SNR, FAR) pairs from the catalog gives a much stronger result: fitting log(SNR) = a + b·log(FAR) and validating via leave-one-out gives a median SNR-prediction error of 10.7% (r = −0.70) — a real, usable relationship, not a weak one. This reverses the earlier conclusion; see Section 8 for the corrected statement.

Accuracy is not uniform across FAR, though. Binning the same leave-one-out results by FAR magnitude:

| FAR range | n | Median SNR-prediction error |
|---|---|---|
| <10⁻⁴/yr (most significant) | 139 | 19.7% |
| 10⁻⁴–10⁻²/yr | 46 | 15.6% |
| 10⁻²–1/yr | 73 | 6.7% |
| >1/yr (least significant) | 123 | 5.6% |

The proxy is *least* accurate for the most significant events — likely because many search pipelines cap reported FAR at a floor value (118 of the 381 events sit at exactly 1×10⁻⁵/yr), collapsing a wide range of true SNRs onto the same FAR reading in that regime.

Applying the proxy downstream — predicting SNR from each circular's own extracted FAR, then feeding that into the physics formula with the same leave-one-out C-fitting procedure used throughout — gives a real but modest improvement on the 49-event circular-only set: median error falls from 44.8% (fixed SNR = 15) to 39.5%, within-±25% rises from 13/49 to 16/49. That is a smaller gain than the FAR-range table above might suggest, and the reason is traceable rather than mysterious: the 49 circular-only events have a median FAR of 4.1×10⁻³/yr — squarely in the harder 15.6%-error band, not the easy 5–6% band. (None of these 49 events are themselves in the catalog yet — they are all more recent than the latest GWTC release — so the proxy's accuracy on this exact population cannot be checked directly; the FAR-stratified result above is the best available evidence for what to expect.)

**Revisiting the combined class+distance model.** Earlier in this investigation, extending the distance-only statistical model with source classification was attempted and abandoned: the 49-event circular-only set is 48/49 (98%) BBH, with no real class diversity to test against. The 214-event catalog-backed set is different — 206 BBH, 5 NSBH, 2 Terrestrial, 1 BNS. Still thin for NSBH/BNS individually (a single-example BNS dummy would have zero degrees of freedom and simply memorize that one point), so classification enters as a single binary predictor (BBH vs. everything else) rather than per-class dummies — a real limitation, stated rather than hidden. On the 212 non-Terrestrial events:

| Model | Median % error | Within ±25% | Within ±50% |
|---|---|---|---|
| Distance only | 27.8% | 98/212 (46%) | 146/212 (69%) |
| Class only (BBH vs. not) | 38.5% | 58/212 (27%) | 135/212 (64%) |
| Distance + class (combined) | 28.9% | 98/212 (46%) | 149/212 (70%) |

This time the answer is clean rather than ambiguous: distance alone is the stronger single predictor, and adding class on top of it does not meaningfully help (28.9% vs. 27.8% median — marginally worse, not better). With real class diversity available, this properly resolves what the 49-event set couldn't test — class does not add independent signal beyond distance, at least at this sample size and with a binary class split.

A second, unplanned finding sits alongside this: distance-only on the larger, more diverse 212-event set (27.8% median) is now competitive with — and by this metric, marginally better than — the physics formula given real catalog SNR (31.5%, Section 6 above). The simplest circular-derivable statistical model matches or exceeds a physically-motivated formula that requires information circulars cannot supply.

**Run-specific calibration (M6.3).** The M6.2 checklist named this as untested: does fitting the physics formula's calibration constant C separately per observing run, instead of one constant across all runs, reduce error? Now that `shared/processing/group_by_event.py` has real per-run date windows (Section 3.2) and the 214-event catalog-backed set spans four runs with real SNR, this is directly testable (`legs/leg1_estimation/validate_run_stratified_calibration.py`), using leave-one-out at every level so no event's own value leaks into its own fold.

| Calibration | Median % error | Within ±25% | Within ±50% |
|---|---|---|---|
| One global C (all 214 events) | 31.5% | 88/214 (41%) | 171/214 (80%) |
| Per-run C (O3a/O3b/O4a/O4b separately) | 26.6% | 97/214 (45%) | 175/214 (82%) |
| Per-era C (O3 vs. O4, merging a/b) | 26.6% | 98/214 (46%) | 177/214 (83%) |

Splitting by run does help — but not uniformly, and the reason why is itself informative. Looking at the fitted C values directly: O3a and O3b fit to C ≈ 8.8–8.9×10⁻⁵, while O4a and O4b fit to C ≈ 5.86–5.90×10⁻⁵ — a genuine ~50% difference between the two observing-run eras, consistent with real detector-network changes (KAGRA joining, sensitivity upgrades) between O3 and O4. But per-run LOO calibration only pays off for the two larger runs (O4a median 32.0%→23.9%, O4b 33.9%→27.3%); it makes the two smaller runs *worse* (O3a 21.1%→33.4%, O3b 25.5%→35.3%), because refitting C via leave-one-out on only 18–25 events is unstable — removing one event shifts the fit more than it does at n=76–94. Merging to era level (O3 vs. O4, n=43 and n=170) recovers essentially all of the run-level benefit while avoiding that small-sample instability, and matches the physical story the fitted-C values themselves tell. Per-era calibration is therefore the version worth keeping, not the finer per-run split.

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

**The physics formula is dominated by an unrecoverable input.** M scales as ρ^1.2, so a factor-of-2 error in assumed SNR produces roughly +130%/−56% error in the mass estimate. Reproducing a mass error within 10–25% requires ρ known to within roughly ±20%; real network SNRs for confident O4a-era detections plausibly span ~8 to 30+, far wider than that tolerance. Holding SNR fixed while distance varies over three orders of magnitude means the physics estimator effectively tracks distance, not mass. This is not a calibration artifact: properly fitting C halves the median error (115% → 45%) but leaves a strong residual bias correlated with distance (r = 0.55, Section 7) — exactly what this sensitivity argument predicts, since C cannot absorb an input the model treats as constant when it physically isn't. Section 6's catalog validation confirms this directly rather than just by argument: giving the same formula real SNR instead of an assumed one, with nothing else changed, cuts median error from 46.6% to 31.5%. A second, smaller lever also confirmed empirically (Section 6, M6.3): the fitted C genuinely differs by observing-run era (≈8.8×10⁻⁵ for O3, ≈5.9×10⁻⁵ for O4, plausibly real detector-network changes), and calibrating separately per era cuts the real-SNR error further, from 31.5% to 26.6% — a real but secondary lever next to SNR itself.

**FAR is a real, usable proxy for SNR — a revision of an earlier, weaker finding.** An initial test using a *back-solved* "required ρ" from the physics formula (the SNR value that would make it match each event's true reference mass) correlated with log(FAR) at only r ≈ −0.34, which looked too weak to be useful. That test was confounded: the back-solved quantity carries the physics formula's own errors along with it. Testing directly against 381 real (SNR, FAR) pairs from the GWTC catalog instead (Section 6) gives r = −0.70 and a 10.7% median SNR-prediction error under leave-one-out validation — a real, fittable relationship. It is *not* uniformly strong, though: accuracy is worst for the most significant events (many pipelines floor their reported FAR, collapsing a range of true SNRs onto one value), and applying the proxy to the 49-event circular-only set (whose FAR values skew toward that harder regime) gives a real but modest downstream improvement (Section 6), not a large one. FAR is a usable, evidenced SNR proxy — just not a precise one across the full significance range.

**The statistical model performs better, but is a different kind of result.** It captures real, exploitable structure (a selection effect between detection distance and mass) rather than a physical single-event inference. A median error of 33% and a 51% correct-bin rate is a meaningfully useful signal — enough to substantially narrow the plausible mass range for a new event before parameter estimation completes — but does not meet a strict 10–25% accuracy target for a majority of events. With real class diversity available in the catalog-backed set, the earlier open question of whether classification adds signal beyond distance is now resolved rather than merely untestable: it does not (Section 6) — distance alone remains the stronger predictor, and at this scale is competitive with the physics formula even when the latter is given real SNR.

### Decision-gate classification

Per the project plan's M6 decision gate (`validated_approximation | useful_constraint | exploratory_only | unsupported`):

- **Physics (SNR-scaling) estimator, circular-only inputs: `unsupported`.** Fails even after properly fitting its calibration constant, with a systematic, physically-explained bias that no calibration choice can remove — because the one input it depends on most (SNR) is structurally absent from circular text. Section 6's catalog validation clarifies the scope of this: the formula itself is not unsupported in the abstract (given real SNR, it more than halves its own error), only as a circular-derived estimator specifically.
- **Statistical (distance-only) estimator: `useful_constraint`.** Not a validated per-event measurement, but a real, reproducible signal (best MAE and bin-hit rate of any method tested) useful for narrowing the plausible mass range. Caveat: a source-class-midpoint baseline with zero fitting is competitive on several metrics (Section 7), so this label credits "distance plus whatever it correlates with," not distance as an independently powerful signal in its own right.

## 9. Limitations

- The circular-only validation set is small (n = 49); leave-one-out cross-validation was used to reduce (not eliminate) overfitting risk given the sample size. The catalog-backed set (Section 6, n = 214) is substantially larger but has its own known limitation: 153 confirmed events are structurally excluded, since low-significance offline catalog additions were never announced via public circular (Section 6).
- Circular-self-reported reference-mass events are, by construction, drawn from later observing runs than O4a, since O4a circulars never report this field. O4a data was used for the availability audit and can be scored by the fitted model, but contributed no circular-only validation examples (the catalog-backed validation set does include O4a events, since the catalog itself has no such reporting gap).
- The regression uses only distance; other circular-derivable fields (FAR, classification) were tested and did not help at this sample size, but may with a larger dataset as the archive grows.
- No independent held-out test set beyond leave-one-out; results should be revisited as more circulars with reference chirp mass accumulate, and as the catalog itself grows.
- Even with real SNR, the physics formula still uses a fixed orientation assumption (cos ι = 0.5, never marginalized or measured), and per-era (not per-run) calibration was the only stratification found stable enough to help (Section 6, M6.3) — finer per-run splits overfit on the two smaller runs (O3a n=25, O3b n=18).

## 10. Open Questions

- Is a 10–25% error target a hard requirement, or a starting point that this data can reasonably revise? (Now more pressing: even with real SNR from the catalog, median error is 31.5%, still outside that band for most events.)
- ~~Would incorporating an external reference catalog (e.g. GWTC/GWOSC) for calibration be an acceptable scope expansion~~ — **resolved**: done (Section 6), on the user's own authorization, pending supervisor sign-off.
- Given the coarse, bin-based nature of the circular-reported ground truth, should "predict the correct bin" replace "predict within X% error" as the primary success metric? (Less relevant for the catalog-backed set, whose reference values are continuous, not binned.)
- Should the thesis report circular-only results as the honest headline finding (matching the original circular-only research question) and catalog-backed results as a supplementary robustness check — or the reverse?
- The FAR→SNR proxy's accuracy on the 49-event circular-only set can't be directly checked (none of those events are in the catalog yet). As more circulars accumulate reference chirp mass and the catalog is periodically updated, this should be re-verified rather than assumed to hold.

## Reproducibility

- Pipeline: `run_pipeline.py` (event table construction) → `data/processed/o4a_event_table.csv`
- Circular-only validation: `validate_estimator.py` → `data/processed/validation_results.csv`
- Catalog-backed validation: `validate_against_catalog.py` → `data/processed/catalog_validation_results.csv` (needs network access to `gwosc.org`; caches results in `data/raw/gwtc_catalog*.json` after first run)
- FAR→SNR proxy: `validate_far_snr_proxy.py` (standalone validation against catalog pairs) and `validate_far_proxy_estimator.py` (applied to the circular-only set)
- Plots: `generate_plots.py` (needs `../../.venv` + matplotlib, see repo root `requirements.txt`)
- Source: `shared/{ingestion,parsing,processing}/`, `legs/leg1_estimation/{modeling,validation,analysis}/`
