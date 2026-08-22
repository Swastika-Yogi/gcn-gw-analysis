"""M6.3 -- Alternative model: run-specific calibration.

Tests one item from the master plan's M6.3 checklist ("run-specific
calibration") that hasn't been tried yet: does fitting a separate physics-
formula calibration constant C per observing run, instead of one global C,
reduce error -- now that shared/processing/group_by_event.py has real
per-run date windows (O3a/O3b/O4a/O4b/O4c) and the 214-event catalog-backed
set (validate_against_catalog.py) supplies real per-event SNR to remove the
confound M6.2 already diagnosed (a fixed assumed SNR).

Uses circular-extracted distance (not the catalog's distance) and real
catalog SNR, mirroring the "estimate from what circulars + a real SNR would
give you" framing used throughout Section 6 of feasibility_draft.md.

Run as: python3 -m legs.leg1_estimation.validate_run_stratified_calibration
"""
import csv
import math
from collections import defaultdict

from legs.leg1_estimation.modeling.chirp_mass_estimator import orientation_factor
from legs.leg1_estimation.validation.metrics import percent_error
from shared.processing.group_by_event import RUN_WINDOWS, in_run_window

INPUT_CSV = "legs/leg1_estimation/data/processed/catalog_validation_results.csv"
ASSUMED_COS_IOTA = 0.5


def event_run(event_id):
    for run, (start, end) in RUN_WINDOWS.items():
        if in_run_window(event_id, start, end):
            return run
    return "unclassified_gap"


def load_rows():
    with open(INPUT_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        out.append({
            "event_id": r["event_id"],
            "run": event_run(r["event_id"]),
            "distance": float(r["circular_distance_mpc"]),
            "snr": float(r["real_snr"]),
            "true_mass": float(r["chirp_mass_source"]),
        })
    return out


def fit_c(rows, cos_iota):
    f_iota = orientation_factor(cos_iota)
    log_c_values = []
    for r in rows:
        x = (r["snr"] * r["distance"]) / f_iota
        log_c_values.append(math.log(r["true_mass"]) - 1.2 * math.log(x))
    return math.exp(sum(log_c_values) / len(log_c_values))


def predict(c, row, cos_iota):
    f_iota = orientation_factor(cos_iota)
    x = (row["snr"] * row["distance"]) / f_iota
    return c * x ** 1.2


def loo_global(rows):
    errors = []
    for i in range(len(rows)):
        train = rows[:i] + rows[i + 1:]
        c = fit_c(train, ASSUMED_COS_IOTA)
        pred = predict(c, rows[i], ASSUMED_COS_IOTA)
        errors.append(percent_error(pred, rows[i]["true_mass"]))
    return errors


def loo_stratified(rows, group_fn, min_group_size=10):
    """LOO calibration fit separately within each group (group_fn maps a
    row to a group label). Groups smaller than min_group_size fall back to
    the global LOO fit, mirroring the "NSBH n=5 too thin for its own dummy"
    reasoning already used for the combined class+distance model."""
    by_group = defaultdict(list)
    for r in rows:
        by_group[group_fn(r)].append(r)

    global_errors = None
    errors_by_id = {}
    fallback_count = 0
    for group, group_rows in by_group.items():
        n = len(group_rows)
        if n < min_group_size:
            if global_errors is None:
                global_errors = loo_global(rows)
                for r, e in zip(rows, global_errors):
                    errors_by_id.setdefault(r["event_id"], e)
            for r in group_rows:
                errors_by_id[r["event_id"]] = errors_by_id[r["event_id"]]
                fallback_count += 1
            continue
        for i in range(n):
            train = group_rows[:i] + group_rows[i + 1:]
            c = fit_c(train, ASSUMED_COS_IOTA)
            pred = predict(c, group_rows[i], ASSUMED_COS_IOTA)
            errors_by_id[group_rows[i]["event_id"]] = percent_error(pred, group_rows[i]["true_mass"])

    errors = [errors_by_id[r["event_id"]] for r in rows]
    return errors, fallback_count


def summarize(errors, label):
    errors_sorted = sorted(errors)
    n = len(errors_sorted)
    median = errors_sorted[n // 2] if n % 2 else (errors_sorted[n // 2 - 1] + errors_sorted[n // 2]) / 2
    within25 = sum(1 for e in errors if e <= 25)
    within50 = sum(1 for e in errors if e <= 50)
    print(f"{label}: n={n}  median={median:.1f}%  within25={within25}/{n}  within50={within50}/{n}")
    return median


def main():
    rows = load_rows()
    print(f"Loaded {len(rows)} events; run distribution:")
    by_run = defaultdict(int)
    for r in rows:
        by_run[r["run"]] += 1
    for run, n in sorted(by_run.items(), key=lambda kv: -kv[1]):
        print(f"  {run}: {n}")
    print()

    def era(r):
        if r["run"] in ("O3a", "O3b"):
            return "O3"
        if r["run"] in ("O4a", "O4b"):
            return "O4"
        return r["run"]

    global_errors = loo_global(rows)
    run_errors, run_fallback = loo_stratified(rows, lambda r: r["run"])
    era_errors, era_fallback = loo_stratified(rows, era)

    summarize(global_errors, "Global C (one constant, all runs)")
    summarize(run_errors, f"Per-run-stratified C ({run_fallback} events fell back to global C, run n<10)")
    summarize(era_errors, f"Era-stratified C, O3 vs O4 ({era_fallback} events fell back to global C)")


if __name__ == "__main__":
    main()
