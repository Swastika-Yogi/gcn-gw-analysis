"""Trivial baseline predictors, per project-plan M7.5.

Neither uses distance, FAR, SNR, or anything estimator-specific - they
exist to answer one question: do the real estimators (physics,
statistical) actually add information, or would a naive guess do just
as well? Both are evaluated the same leave-one-out way as the real
estimators, using only the training fold to avoid leakage.
"""
import math

from legs.leg1_estimation.validation.metrics import bin_hit, percent_error

# Typical chirp-mass midpoints by source class (M_sun), consistent with the
# bin structure LVK circulars report against (see mass_parser.py).
CLASS_MIDPOINT = {
    "BBH": 33.0,
    "NSBH": 5.5,
    "BNS": 1.3,
}
DEFAULT_MIDPOINT = 8.25  # used when source_class is unknown for an event


def class_midpoint_predictions(rows):
    """Predict a fixed typical mass for the event's classified source type,
    ignoring distance/FAR/everything else. No fitting - nothing to leak."""
    results = []
    for r in rows:
        predicted = CLASS_MIDPOINT.get(r.get("source_class"), DEFAULT_MIDPOINT)
        true = r["reference_chirp_mass"]
        results.append({
            "event_id": r["event_id"],
            "predicted_msun": predicted,
            "reference_msun": round(true, 3),
            "percent_error": round(percent_error(predicted, true), 1),
            "bin_hit": bin_hit(predicted, r["reference_chirp_mass_low"], r["reference_chirp_mass_high"]),
        })
    return results


def population_average_predictions(rows):
    """Predict the training-fold mean reference mass for every held-out event.

    Leave-one-out, same as the real estimators: the mean excludes the event
    being predicted, so this isn't just reporting in-sample fit.
    """
    n = len(rows)
    total = sum(r["reference_chirp_mass"] for r in rows)

    results = []
    for i, r in enumerate(rows):
        predicted = (total - r["reference_chirp_mass"]) / (n - 1)
        true = r["reference_chirp_mass"]
        results.append({
            "event_id": r["event_id"],
            "predicted_msun": round(predicted, 3),
            "reference_msun": round(true, 3),
            "percent_error": round(percent_error(predicted, true), 1),
            "bin_hit": bin_hit(predicted, r["reference_chirp_mass_low"], r["reference_chirp_mass_high"]),
        })
    return results
