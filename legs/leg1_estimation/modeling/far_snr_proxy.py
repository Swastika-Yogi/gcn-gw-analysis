"""FAR -> SNR proxy, fit and validated against real (SNR, FAR) pairs from
the GWTC catalog (see validation/load_reference_catalog.py).

Project context section 9.1 warns against inferring SNR from FAR "without
a defensible mapping." This module IS that defensible mapping - fit and
leave-one-out validated against 381 real (SNR, FAR) pairs, not assumed.
Earlier in this project (feasibility_draft.md Section 8/Discussion), a much
weaker version of this idea was tested using a back-solved "required rho"
proxy on only 49 circular-only events (r = -0.34) and found too weak to be
useful. With real measured SNR now available from the catalog, the same
relationship is far stronger (r = -0.70, n = 381) - worth revisiting.

Model: log(SNR) = a + b * log(FAR), ordinary least squares.
"""
import math

from legs.leg1_estimation.modeling.statistical_estimator import fit_log_linear, predict_log_linear

HZ_PER_YEAR = 365.25 * 24 * 3600  # for converting circular-extracted FAR (Hz) to catalog units (1/yr)


def far_hz_to_per_year(far_hz):
    return far_hz * HZ_PER_YEAR


def fit_proxy(far_per_year_values, snr_values):
    """far_per_year_values, snr_values: parallel lists of real (FAR, SNR)
    pairs, FAR already in 1/yr. Returns (a, b) for log(SNR) = a + b*log(FAR)."""
    log_far = [math.log(f) for f in far_per_year_values]
    log_snr = [math.log(s) for s in snr_values]
    return fit_log_linear([log_far], log_snr)


def predict_snr(coefficients, far_per_year):
    return math.exp(predict_log_linear(coefficients, [math.log(far_per_year)]))
