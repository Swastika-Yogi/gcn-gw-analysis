"""Apply the baseline chirp-mass estimator (PDF sections 5-11) to an event table.

SNR and orientation aren't available per-event from circulars (project
context section 9.1/9.2), so this uses the same fixed assumptions the PDF
itself validated its worked example against: snr=15 (consistent with a
high-confidence, low-FAR detection), cos(iota)=0.5 (typical/non-extreme
orientation), and C=1e-4 (the PDF's own calibration from known GW events).
These are NOT re-fit here - section 9.3 requires fitting C against a real
reference set, which isn't possible for O4a (no reference_chirp_mass in
circulars for this run). Treat every value produced here as illustrative,
not validated, until that calibration step happens.
"""
from src.modeling.chirp_mass_estimator import estimate_chirp_mass

ASSUMED_SNR = 15
ASSUMED_COS_IOTA = 0.5
ASSUMED_C = 1e-4

ASSUMPTION_NOTE = (
    f"assumed snr={ASSUMED_SNR}, cos_iota={ASSUMED_COS_IOTA}, C={ASSUMED_C} "
    "(uncalibrated for O4a - no in-circular reference chirp mass to fit against)"
)


def add_chirp_mass_estimates(rows):
    for row in rows:
        distance = row.get("luminosity_distance_mpc")
        if distance in (None, ""):
            row["estimated_chirp_mass_msun"] = "N/A"
            row["estimation_notes"] = "N/A - no luminosity distance extracted"
            continue

        estimate = estimate_chirp_mass(
            distance_mpc=float(distance),
            snr=ASSUMED_SNR,
            calibration_constant=ASSUMED_C,
            cos_iota=ASSUMED_COS_IOTA,
        )
        row["estimated_chirp_mass_msun"] = round(estimate, 2)
        row["estimation_notes"] = ASSUMPTION_NOTE

    return rows
