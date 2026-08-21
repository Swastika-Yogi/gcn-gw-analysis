"""Validate both chirp-mass estimators against circulars that self-report a
reference value (any run - O4a alone has none, see project context).

Physics formula (chirp_mass_estimator.py, fixed SNR=15 assumption) vs.
statistical model (statistical_estimator.py, log-linear on distance) -
see the feasibility memo for why SNR being unrecoverable makes the physics
formula the weaker of the two on real data.

Run from the repo root as a module: `python3 -m legs.leg1_estimation.validate_estimator`
"""
import csv
import math

from shared.ingestion.load_gcn_archive import download_and_extract, load_circulars
from legs.leg1_estimation.modeling.apply_estimator import ASSUMED_C, ASSUMED_COS_IOTA, ASSUMED_SNR
from legs.leg1_estimation.modeling.baselines import class_midpoint_predictions, population_average_predictions
from legs.leg1_estimation.modeling.calibration import bias_test, loo_calibrated_predictions
from legs.leg1_estimation.modeling.chirp_mass_estimator import estimate_chirp_mass
from shared.processing.build_event_table import build_event_table
from shared.processing.group_by_event import filter_gw_circulars, group_by_event
from legs.leg1_estimation.validation.build_validation_set import build_validation_set
from legs.leg1_estimation.validation.metrics import bin_hit, leave_one_out, percent_error, summarize

OUTPUT_CSV = "legs/leg1_estimation/data/processed/validation_results.csv"


def print_summary(label, summary):
    if summary["n"] == 0:
        print(f"{label}: no data")
        return
    hits, n = summary["within_25pct"]
    bhits, bn = summary["bin_hit_rate"]
    print(
        f"{label:<42} median={summary['median_percent_error']:>6.1f}%  "
        f"within25={hits:>2}/{n}  bin-hit={bhits:>2}/{bn}  max={summary['max_percent_error']:>6.1f}%"
    )
    print(
        f"{'':<42} MAE={summary['mae_msun']:>6.2f} Msun  "
        f"RMSE={summary['rmse_msun']:>6.2f} Msun  bias={summary['bias_msun']:>+6.2f} Msun"
    )


def main():
    folder_path = download_and_extract()
    circulars = load_circulars(folder_path)
    gw_circulars = filter_gw_circulars(circulars)

    event_to_circulars = group_by_event(gw_circulars)  # no run window: all runs
    rows, _ = build_event_table(event_to_circulars)

    val = build_validation_set(rows)
    print(f"Validation set: {len(val)} events (all runs, self-reported reference chirp mass, non-Terrestrial)\n")

    log_targets = [math.log(r["reference_chirp_mass"]) for r in val]
    log_distance = [math.log(r["luminosity_distance_mpc"]) for r in val]

    # --- statistical model: log(mass) ~ log(distance) ---
    stat_results = leave_one_out([log_distance], log_targets, val)
    print_summary("Statistical: log(M) ~ log(distance)", summarize(stat_results))

    # --- physics formula baseline, fixed snr/orientation/C ---
    physics_results = []
    for r in val:
        predicted = estimate_chirp_mass(
            r["luminosity_distance_mpc"], ASSUMED_SNR, ASSUMED_C, ASSUMED_COS_IOTA
        )
        true = r["reference_chirp_mass"]
        physics_results.append({
            "event_id": r["event_id"],
            "predicted_msun": round(predicted, 3),
            "reference_msun": round(true, 3),
            "percent_error": round(percent_error(predicted, true), 1),
            "bin_hit": bin_hit(predicted, r["reference_chirp_mass_low"], r["reference_chirp_mass_high"]),
        })
    print_summary(f"Physics: fixed SNR={ASSUMED_SNR}, C={ASSUMED_C} (uncalibrated)", summarize(physics_results))

    # --- physics formula, but C fit per-fold on training events only (M6.2) ---
    calibrated_results, fitted_c_values = loo_calibrated_predictions(val, ASSUMED_SNR, ASSUMED_COS_IOTA)
    print_summary(f"Physics: fixed SNR={ASSUMED_SNR}, C fit per-fold (LOO)", summarize(calibrated_results))

    fitted_c_values.sort()
    n = len(fitted_c_values)
    print(
        f"  fitted C across folds: median={fitted_c_values[n // 2]:.2e}  "
        f"min={fitted_c_values[0]:.2e}  max={fitted_c_values[-1]:.2e}  "
        f"(vs methodology note's fixed C={ASSUMED_C:.2e})"
    )
    bias = bias_test(calibrated_results, val)
    print(f"  systematic bias (correlation of log-distance with log-residual): {bias:.3f}")

    # --- trivial baselines (M7.5): do the real estimators beat naive guessing? ---
    print()
    class_results = class_midpoint_predictions(val)
    print_summary("Baseline: source-class midpoint", summarize(class_results))
    pop_results = population_average_predictions(val)
    print_summary("Baseline: population average (LOO)", summarize(pop_results))

    with open(OUTPUT_CSV, "w", newline="") as f:
        fieldnames = ["event_id", "statistical_predicted_msun", "physics_predicted_msun",
                      "physics_calibrated_predicted_msun", "reference_msun",
                      "statistical_pct_error", "physics_pct_error", "physics_calibrated_pct_error",
                      "statistical_bin_hit", "physics_bin_hit", "physics_calibrated_bin_hit"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s, p, c in zip(stat_results, physics_results, calibrated_results):
            writer.writerow({
                "event_id": s["event_id"],
                "statistical_predicted_msun": s["predicted_msun"],
                "physics_predicted_msun": p["predicted_msun"],
                "physics_calibrated_predicted_msun": c["predicted_msun"],
                "reference_msun": s["reference_msun"],
                "statistical_pct_error": s["percent_error"],
                "physics_pct_error": p["percent_error"],
                "physics_calibrated_pct_error": c["percent_error"],
                "statistical_bin_hit": s["bin_hit"],
                "physics_bin_hit": p["bin_hit"],
                "physics_calibrated_bin_hit": c["bin_hit"],
            })
    print("\nPer-event results saved to:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
