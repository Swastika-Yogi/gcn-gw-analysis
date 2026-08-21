"""Experiment A: data-availability report (project context section 14)."""


def data_availability_report(rows):
    n = len(rows)
    if n == 0:
        return {"n_events": 0}

    def pct(field):
        count = sum(1 for r in rows if r.get(field) is not None)
        return count, round(100 * count / n, 1)

    dist_count, dist_pct = pct("luminosity_distance_mpc")
    far_count, far_pct = pct("far_value")
    class_count, class_pct = pct("source_class")
    mass_count, mass_pct = pct("reference_chirp_mass")

    complete_case = sum(
        1 for r in rows
        if r.get("luminosity_distance_mpc") is not None and r.get("far_value") is not None
    )

    return {
        "n_events": n,
        "with_distance": (dist_count, dist_pct),
        "with_far": (far_count, far_pct),
        "with_classification": (class_count, class_pct),
        "with_reference_chirp_mass": (mass_count, mass_pct),
        "complete_case_distance_and_far": (complete_case, round(100 * complete_case / n, 1)),
    }


def print_report(report, label=""):
    if label:
        print(f"\n--- Data availability: {label} ---")
    print("Events:", report["n_events"])
    if report["n_events"] == 0:
        return
    print(f"  with distance:              {report['with_distance'][0]}/{report['n_events']} ({report['with_distance'][1]}%)")
    print(f"  with FAR:                   {report['with_far'][0]}/{report['n_events']} ({report['with_far'][1]}%)")
    print(f"  with classification:        {report['with_classification'][0]}/{report['n_events']} ({report['with_classification'][1]}%)")
    print(f"  with reference chirp mass:  {report['with_reference_chirp_mass'][0]}/{report['n_events']} ({report['with_reference_chirp_mass'][1]}%)")
    print(f"  complete case (dist+FAR):   {report['complete_case_distance_and_far'][0]}/{report['n_events']} ({report['complete_case_distance_and_far'][1]}%)")
