"""Fit and validate the physics formula's calibration constant C, per
project-plan M6.2: "Fit C using training events. Hold out validation
events. Estimate uncertainty in C. Test systematic bias."

Previously C was taken directly from the methodology note (1e-4, fit on
one worked example) and used unchanged everywhere. That's not a fitted
calibration - it's an assumption. This module fits C properly.

Given fixed assumed SNR and orientation (still required - see
chirp_mass_estimator.py's docstring on why those can't be per-event),
the formula M = C * (rho * D_L / F)^1.2 has exactly one free parameter:
the exponent 1.2 is fixed by the physics, so fitting C in log-space is
just the mean residual - a 1-parameter fit, not a full regression.
"""
import math

from src.modeling.chirp_mass_estimator import orientation_factor


def fit_c(rows, snr, cos_iota):
    """Closed-form fit: C = geometric mean of (true_M / (rho*D_L/F)^1.2)."""
    f_iota = orientation_factor(cos_iota)
    log_c_values = []
    for r in rows:
        x = (snr * r["luminosity_distance_mpc"]) / f_iota
        log_c_values.append(math.log(r["reference_chirp_mass"]) - 1.2 * math.log(x))
    return math.exp(sum(log_c_values) / len(log_c_values))


def loo_calibrated_predictions(rows, snr, cos_iota):
    """Leave-one-out: fit C on all-but-one, predict the held-out event.

    Mirrors the split methodology already used for the statistical model
    (src/validation/metrics.py's leave_one_out), so the two estimators are
    compared on equal footing rather than one using in-sample calibration.

    Returns (results, fitted_c_values) - fitted_c_values is the C obtained
    in each fold, i.e. an empirical distribution giving C's uncertainty
    across the 49-event sample.
    """
    from src.validation.metrics import bin_hit, percent_error

    f_iota = orientation_factor(cos_iota)
    n = len(rows)
    results = []
    fitted_c_values = []

    for i in range(n):
        train = rows[:i] + rows[i + 1:]
        c = fit_c(train, snr, cos_iota)
        fitted_c_values.append(c)

        r = rows[i]
        predicted = c * ((snr * r["luminosity_distance_mpc"]) / f_iota) ** 1.2
        true = r["reference_chirp_mass"]

        results.append({
            "event_id": r["event_id"],
            "predicted_msun": round(predicted, 3),
            "reference_msun": round(true, 3),
            "percent_error": round(percent_error(predicted, true), 1),
            "bin_hit": bin_hit(predicted, r["reference_chirp_mass_low"], r["reference_chirp_mass_high"]),
            "fitted_c": c,
            "log_residual": math.log(predicted) - math.log(true),
        })

    return results, fitted_c_values


def bias_test(results, rows):
    """Correlation between log(distance) and log-residual across LOO folds.

    A strong correlation means the constant-C model is systematically
    biased by distance - i.e. it isn't really capturing mass, it's
    capturing distance, consistent with the fixed-SNR sensitivity finding.
    """
    log_dist = [math.log(r["luminosity_distance_mpc"]) for r in rows]
    residuals = [res["log_residual"] for res in results]
    n = len(residuals)
    mean_x = sum(log_dist) / n
    mean_y = sum(residuals) / n
    cov = sum((log_dist[i] - mean_x) * (residuals[i] - mean_y) for i in range(n)) / n
    sx = (sum((x - mean_x) ** 2 for x in log_dist) / n) ** 0.5
    sy = (sum((y - mean_y) ** 2 for y in residuals) / n) ** 0.5
    return cov / (sx * sy) if sx > 0 and sy > 0 else float("nan")
