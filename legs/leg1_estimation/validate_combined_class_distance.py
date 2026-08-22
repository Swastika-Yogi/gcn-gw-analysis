"""Revisit the combined class+distance statistical model, now that the
214-event catalog-backed set has real class diversity (206 BBH, 5 NSBH,
2 Terrestrial, 1 BNS) unlike the old 49-event circular-only set (48/49
BBH), which is why this was explicitly rejected earlier - see
feasibility_draft.md's "Rejected / walked back" note and
docs/progress_log.md 2026-08-22.

Modeling choice: NSBH (n=5) and BNS (n=1) are still too thin for their
own per-class dummies (a 1-example dummy has zero degrees of freedom
and would just memorize that point). Using a single is_bbh binary
predictor (BBH vs. everything else) instead - defensible given the
sample sizes, and stated as a limitation, not hidden.

Terrestrial events (n=2) are excluded throughout, per the same policy
already applied to the 49-event set (noise triggers, not real sources).

Run: python3 -m legs.leg1_estimation.validate_combined_class_distance
"""
import csv
import math

from legs.leg1_estimation.modeling.statistical_estimator import fit_log_linear, predict_log_linear

INPUT_CSV = "legs/leg1_estimation/data/processed/catalog_validation_results.csv"


def load_rows():
    with open(INPUT_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if r["source_class"] != "Terrestrial"]


def loo_cv(predictor_columns, log_targets, true_values):
    n = len(log_targets)
    errors = []
    for i in range(n):
        train_cols = [col[:i] + col[i + 1:] for col in predictor_columns]
        train_targets = log_targets[:i] + log_targets[i + 1:]
        coef = fit_log_linear(train_cols, train_targets)
        test_values = [col[i] for col in predictor_columns]
        pred = math.exp(predict_log_linear(coef, test_values))
        true = true_values[i]
        errors.append(abs(pred - true) / true * 100)
    return errors


def summarize(errors, label):
    errors_sorted = sorted(errors)
    n = len(errors_sorted)
    within25 = sum(1 for e in errors_sorted if e <= 25)
    within50 = sum(1 for e in errors_sorted if e <= 50)
    print(f"{label:<45} median={errors_sorted[n // 2]:>6.1f}%  within25={within25:>3}/{n}  within50={within50:>3}/{n}  max={errors_sorted[-1]:>6.1f}%")


def main():
    rows = load_rows()
    print(f"Catalog-backed set, Terrestrial excluded: {len(rows)} events\n")

    true_masses = [float(r["chirp_mass_source"]) for r in rows]
    log_mass = [math.log(m) for m in true_masses]
    log_dist = [math.log(float(r["circular_distance_mpc"])) for r in rows]
    is_bbh = [1.0 if r["source_class"] == "BBH" else 0.0 for r in rows]

    errs_dist_only = loo_cv([log_dist], log_mass, true_masses)
    summarize(errs_dist_only, "Distance only")

    errs_class_only = loo_cv([is_bbh], log_mass, true_masses)
    summarize(errs_class_only, "Class only (is_bbh)")

    errs_combined = loo_cv([log_dist, is_bbh], log_mass, true_masses)
    summarize(errs_combined, "Distance + class (combined)")

    print()
    print("For reference (physics formula, real catalog SNR, same-ish population): 31.5% median")


if __name__ == "__main__":
    main()
