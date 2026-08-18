"""Baseline chirp-mass estimator from the methodology note (PDF sections 2-7).

    M_z = C * (rho * D_L / F(iota)) ** (6/5)

All physical assumptions are explicit arguments - see project context
section 9: nothing here is silently hardcoded as a hidden default. SNR is
not directly available in circulars (section 9.1), so this module always
requires it as an explicit value or range from the caller; it is never
inferred from FAR.
"""


def orientation_factor(cos_iota):
    """F(iota) = [(1 + cos^2(iota)) / 2] (project context section 8 (iii),
    using the +-polarization-only simplification from the PDF)."""
    return (1 + cos_iota ** 2) / 2


def estimate_chirp_mass(distance_mpc, snr, calibration_constant, cos_iota=0.5, mass_frame="detector"):
    """Single-point estimate for one (snr, orientation) assumption.

    mass_frame is recorded, not derived: this formula estimates M_z
    (detector-frame / redshifted chirp mass, see PDF section 3 and project
    context section 5) unless the caller has independently converted it.
    """
    if mass_frame != "detector":
        raise ValueError(
            "estimate_chirp_mass only implements the detector-frame (M_z) "
            "relation from the methodology note; pass mass_frame='detector' "
            "or convert the result yourself using an explicit redshift."
        )

    f_iota = orientation_factor(cos_iota)
    return calibration_constant * ((snr * distance_mpc) / f_iota) ** (6 / 5)


def estimate_chirp_mass_range(distance_mpc, snr_range, calibration_constant, cos_iota=0.5):
    """Sensitivity-range estimate: one M_z per SNR value in snr_range.

    Per project-context Experiment C, when SNR isn't extracted from a
    circular we evaluate across a plausible range instead of assuming one
    fixed value.
    """
    return [
        estimate_chirp_mass(distance_mpc, snr, calibration_constant, cos_iota)
        for snr in snr_range
    ]


DEFAULT_SNR_RANGE = range(8, 26)  # detection threshold (~8) through high-confidence (~25)
