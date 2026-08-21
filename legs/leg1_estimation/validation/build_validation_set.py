"""Build the validation set: events where circulars self-report a reference
chirp mass (any run, not just O4a - see project context, O4a itself has none).

Terrestrial-classified events are excluded: they're noise triggers, and
"chirp mass" isn't a meaningful astrophysical quantity for them, even
though the low-latency pipeline still assigns a bin.
"""


def build_validation_set(rows, require_far=True):
    val = [
        r for r in rows
        if r.get("reference_chirp_mass") is not None
        and r.get("luminosity_distance_mpc") is not None
        and r.get("source_class") != "Terrestrial"
    ]
    if require_far:
        val = [r for r in val if r.get("far_value") is not None]
    return val
