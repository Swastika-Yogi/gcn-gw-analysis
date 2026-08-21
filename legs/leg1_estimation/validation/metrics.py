"""Metrics for comparing an estimated chirp mass against the circular's own
reported reference value.

Two metrics, because the reference value itself is coarse: LVK's
low-latency pipeline reports chirp mass as a bin midpoint (bins are
roughly log-spaced, ~2x wide), not a continuous measurement. Percentage
error judges against that midpoint; bin-hit judges against the actual
reported bin bounds for that event, which is arguably the more honest
target given how coarse the ground truth already is.
"""
import math


def percent_error(predicted, true):
    return abs(predicted - true) / true * 100


def bin_hit(predicted, low, high):
    return low <= predicted <= high


def leave_one_out(predictor_columns, log_targets, rows):
    """Fits fit_log_linear on all-but-one, predicts the held-out event, repeats.

    rows must align index-for-index with log_targets/predictor_columns.
    Returns a list of per-event result dicts.
    """
    from legs.leg1_estimation.modeling.statistical_estimator import fit_log_linear, predict_log_linear

    n = len(log_targets)
    results = []
    for i in range(n):
        train_cols = [col[:i] + col[i + 1:] for col in predictor_columns]
        train_targets = log_targets[:i] + log_targets[i + 1:]
        coefficients = fit_log_linear(train_cols, train_targets)

        test_values = [col[i] for col in predictor_columns]
        predicted = math.exp(predict_log_linear(coefficients, test_values))
        true = math.exp(log_targets[i])
        row = rows[i]

        results.append({
            "event_id": row["event_id"],
            "predicted_msun": round(predicted, 3),
            "reference_msun": round(true, 3),
            "percent_error": round(percent_error(predicted, true), 1),
            "bin_hit": bin_hit(predicted, row["reference_chirp_mass_low"], row["reference_chirp_mass_high"]),
        })
    return results


def summarize(results):
    n = len(results)
    if n == 0:
        return {"n": 0}
    errors = sorted(r["percent_error"] for r in results)
    within_25 = sum(1 for e in errors if e <= 25)
    bin_hits = sum(1 for r in results if r["bin_hit"])

    # signed_error > 0 means the estimator over-predicts mass for that event
    signed_errors = [r["predicted_msun"] - r["reference_msun"] for r in results]
    absolute_errors = [abs(e) for e in signed_errors]
    mae = sum(absolute_errors) / n
    rmse = (sum(e ** 2 for e in signed_errors) / n) ** 0.5
    bias = sum(signed_errors) / n

    return {
        "n": n,
        "median_percent_error": errors[n // 2],
        "max_percent_error": errors[-1],
        "within_25pct": (within_25, n),
        "bin_hit_rate": (bin_hits, n),
        "mae_msun": round(mae, 2),
        "rmse_msun": round(rmse, 2),
        "bias_msun": round(bias, 2),
    }
