"""M4.4 -- Extraction evaluation: a manually annotated gold-sample audit.

Two fixed samples, drawn once (seeded) and hand-annotated by reading each
circular's raw text directly rather than trusting parser output:

1. `GENERAL_SAMPLE` (circular IDs) -- 30 circulars drawn from the
   identification+update pool across the whole archive (the two circular
   types that carry almost all real field content, per Section 3.2's
   by-circular-type breakdown). Covers distance, FAR, classification.
2. `O4C_MASS_SAMPLE` (circular IDs) -- 15 identification circulars drawn
   from O4c specifically, since the reference-chirp-mass bin sentence is
   completely absent before O4c (Section 3.2); the general sample alone
   has zero positives for this field and can't support a meaningful
   precision/recall estimate.

Ground truth (GOLD dict) was recorded by reading each circular's text,
noting whether each field is genuinely present and what its true value is,
*before* comparing to the parser's output. Two findings from that process
are recorded as comments next to the specific entries that produced them,
and both are written up in `docs/feasibility_draft.md` (Section 2.1):
  - a real bug in `far_parser.py` (bare, case-insensitive "far" collided
    with ordinary English "so far"/"as far as"), found here and fixed.
  - a circular whose "distance" match is a directionally-conditioned
    posterior value (DISTMU) rather than the whole-sky-marginalized
    luminosity distance other circulars report -- a genuine ambiguity,
    not a bug, left as a documented edge case.

Run as: python3 -m legs.leg1_estimation.analysis.gold_sample_audit
(requires the archive to already be downloaded, see run_pipeline.py)
"""
from shared.ingestion.load_gcn_archive import download_and_extract, load_circulars, circular_text
from shared.parsing import classification_parser, distance_parser, far_parser, mass_parser

GENERAL_SAMPLE = [
    38303, 38720, 36236, 37743, 25773, 34124, 21568, 34337, 38744, 25087,
    38065, 27036, 26350, 25497, 25094, 34606, 25549, 35018, 27130, 34494,
    26507, 36847, 34975, 39506, 18442, 39238, 37268, 37587, 25753, 35168,
]

O4C_MASS_SAMPLE = [
    39506, 39201, 42462, 41638, 40935, 41155, 41336, 41601, 42624, 42357,
    41700, 41810, 40879, 41179, 39155,
]

GOLD = {
    38303: dict(distance_present=True, distance_val=2267, far_present=False, far_val=None,
                class_present=True, source_class="BBH"),
    38720: dict(distance_present=True, distance_val=2008, far_present=False, far_val=None,
                class_present=False, source_class=None),
    36236: dict(distance_present=True, distance_val=214, far_present=True, far_val=3.1e-13,
                class_present=True, source_class="NSBH"),
    37743: dict(distance_present=True, distance_val=6642, far_present=True, far_val=3.3e-08,
                class_present=True, source_class="BBH"),
    25773: dict(distance_present=True, distance_val=1584, far_present=False, far_val=None,
                class_present=False, source_class=None),
    34124: dict(distance_present=True, distance_val=8710, far_present=True, far_val=2.4e-08,
                class_present=True, source_class="BBH"),
    # G-event / IceCube neutrino follow-up. Subject line "LIGO/Virgo G298048:
    # UPDATE on IceCube neutrino candidates" is not LVK-authored despite the
    # LVK-style subject prefix -- caused the M5.1 circular-type classifier
    # (subject-pattern based) to mislabel it as an "update" circular.
    21568: dict(distance_present=False, distance_val=None, far_present=False, far_val=None,
                class_present=False, source_class=None),
    34337: dict(distance_present=True, distance_val=3852, far_present=True, far_val=9.2e-09,
                class_present=True, source_class="BBH"),
    38744: dict(distance_present=True, distance_val=830, far_present=False, far_val=None,
                class_present=False, source_class=None),
    25087: dict(distance_present=True, distance_val=227, far_present=True, far_val=3.6e-08,
                class_present=True, source_class="Terrestrial"),
    38065: dict(distance_present=True, distance_val=364, far_present=False, far_val=None,
                class_present=False, source_class=None),
    27036: dict(distance_present=True, distance_val=2142, far_present=False, far_val=None,
                class_present=False, source_class=None),
    26350: dict(distance_present=True, distance_val=385, far_present=True, far_val=1.2e-08,
                class_present=True, source_class="NSBH"),
    25497: dict(distance_present=True, distance_val=2276, far_present=True, far_val=8.5e-22,
                class_present=True, source_class="BBH"),
    # Archived body has "926 <replacement-char> 259 Mpc" -- the +/- symbol is
    # corrupted (an archive-side encoding artifact, not a pipeline bug). The
    # high-confidence value+/-error regex correctly fails to match it; the
    # medium-confidence fallback still recovers the central value (926) but
    # silently drops the real uncertainty bound, with no signal distinguishing
    # this from an event that genuinely has no reported uncertainty.
    25094: dict(distance_present=True, distance_val=926, far_present=False, far_val=None,
                class_present=False, source_class=None),
    34606: dict(distance_present=True, distance_val=4900, far_present=False, far_val=None,
                class_present=False, source_class=None),
    25549: dict(distance_present=False, distance_val=None, far_present=True, far_val=1.9e-08,
                class_present=True, source_class="Terrestrial"),
    35018: dict(distance_present=True, distance_val=3260, far_present=False, far_val=None,
                class_present=False, source_class=None),
    27130: dict(distance_present=True, distance_val=1510, far_present=True, far_val=1.3e-08,
                class_present=True, source_class="BBH"),
    34494: dict(distance_present=True, distance_val=4872, far_present=True, far_val=8.8e-09,
                class_present=True, source_class="BBH"),
    # GROWTH-collaboration galaxy cross-match (not LVK-authored; same
    # subject-prefix mislabeling as 21568 above). Body does contain the
    # literal word "distance" ("The distance parameters from the LALInference
    # localization ... are DISTMU= 272.35 Mpc") -- a direction-conditioned
    # posterior distance at the external candidate's sky position, not the
    # whole-sky-marginalized luminosity distance LVK circulars report. The
    # parser's match is defensible given its own definition of "distance
    # near a number", not a clean false positive; recorded as an edge case.
    26507: dict(distance_present=True, distance_val=272.35, far_present=False, far_val=None,
                class_present=False, source_class=None),
    36847: dict(distance_present=True, distance_val=1249, far_present=False, far_val=None,
                class_present=False, source_class=None),
    34975: dict(distance_present=True, distance_val=1949, far_present=True, far_val=1.9e-08,
                class_present=True, source_class="BBH"),
    39506: dict(distance_present=True, distance_val=2077, far_present=True, far_val=2.6e-12,
                class_present=True, source_class="BBH"),
    18442: dict(distance_present=False, distance_val=None, far_present=True, far_val=9.65e-08,
                class_present=False, source_class=None),
    39238: dict(distance_present=True, distance_val=918, far_present=False, far_val=None,
                class_present=False, source_class=None),
    37268: dict(distance_present=True, distance_val=1342, far_present=True, far_val=3.2e-09,
                class_present=True, source_class="BBH"),
    37587: dict(distance_present=True, distance_val=1169, far_present=True, far_val=1.4e-24,
                class_present=True, source_class="BBH"),
    25753: dict(distance_present=True, distance_val=1557, far_present=True, far_val=9.7e-10,
                class_present=True, source_class="BBH"),
    35168: dict(distance_present=True, distance_val=1148, far_present=True, far_val=3.2e-10,
                class_present=True, source_class="BBH"),
}

# Chirp-mass ground truth for the O4c-stratified sample: (present, low, high) or None.
MASS_GOLD = {
    39506: None,
    39201: None,
    42462: (5.5, 11.0),
    41638: (11.0, 22.0),
    40935: (5.5, 11.0),
    41155: (11.0, 22.0),
    41336: (22.0, 44.0),
    41601: (22.0, 44.0),
    42624: (22.0, 44.0),
    42357: (22.0, 44.0),
    41700: (11.0, 22.0),
    41810: (44.0, 88.0),
    40879: (22.0, 44.0),
    41179: (22.0, 44.0),
    39155: None,
}


def _confusion(gold_present, pred_present, tp, fp, fn, tn):
    if gold_present and pred_present:
        tp += 1
    elif gold_present and not pred_present:
        fn += 1
    elif not gold_present and pred_present:
        fp += 1
    else:
        tn += 1
    return tp, fp, fn, tn


def _prf1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else float("nan")
    r = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = 2 * p * r / (p + r) if (p + r) else float("nan")
    return p, r, f1


def main():
    download_and_extract()
    circulars = {data.get("circularId"): data for _, data in load_circulars()}

    counts = {f: [0, 0, 0, 0] for f in ("distance", "far", "classification")}
    for cid in GENERAL_SAMPLE:
        text = circular_text(circulars[cid])
        gold = GOLD[cid]

        dist = distance_parser.extract_distance(text)
        far = far_parser.extract_far(text)
        cls = classification_parser.extract_classification(text)

        counts["distance"] = list(_confusion(gold["distance_present"], bool(dist), *counts["distance"]))
        counts["far"] = list(_confusion(gold["far_present"], bool(far), *counts["far"]))
        counts["classification"] = list(_confusion(gold["class_present"], cls is not None, *counts["classification"]))

    mass_tp = mass_fp = mass_fn = mass_tn = 0
    for cid in O4C_MASS_SAMPLE:
        text = circular_text(circulars[cid])
        gold_present = MASS_GOLD[cid] is not None
        pred = mass_parser.extract_chirp_mass_bin(text)
        pred_present = bool(pred)
        mass_tp, mass_fp, mass_fn, mass_tn = _confusion(gold_present, pred_present, mass_tp, mass_fp, mass_fn, mass_tn)
        if gold_present and pred:
            assert (pred[0]["low"], pred[0]["high"]) == MASS_GOLD[cid], (cid, pred, MASS_GOLD[cid])

    print(f"=== M4.4 gold-sample audit (n={len(GENERAL_SAMPLE)} general + {len(O4C_MASS_SAMPLE)} O4c-mass) ===\n")
    for field in ("distance", "far", "classification"):
        tp, fp, fn, tn = counts[field]
        p, r, f1 = _prf1(tp, fp, fn)
        print(f"{field:16s} TP={tp:2d} FP={fp:2d} FN={fn:2d} TN={tn:2d}  precision={p:.2f} recall={r:.2f} F1={f1:.2f}")
    p, r, f1 = _prf1(mass_tp, mass_fp, mass_fn)
    print(f"{'chirp_mass':16s} TP={mass_tp:2d} FP={mass_fp:2d} FN={mass_fn:2d} TN={mass_tn:2d}  precision={p:.2f} recall={r:.2f} F1={f1:.2f}  (O4c-stratified sample)")


if __name__ == "__main__":
    main()
