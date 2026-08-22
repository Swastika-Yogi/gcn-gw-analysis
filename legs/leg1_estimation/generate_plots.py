"""M7.4: required validation plots, one set per estimator.

Reads legs/leg1_estimation/data/processed/validation_results.csv (produced
by validate_estimator.py) and saves four plots per estimator into
legs/leg1_estimation/figures/:
  - <estimator>_scatter.png   - estimated vs reference, with a y=x line
  - <estimator>_residual.png  - residual (predicted - true) vs predicted
  - <estimator>_histogram.png - distribution of percent error
  - <estimator>_vs_distance.png - percent error vs distance

Run via the project venv (matplotlib isn't in the system Python):
  ./.venv/bin/python -m legs.leg1_estimation.generate_plots
"""
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INPUT_CSV = "legs/leg1_estimation/data/processed/validation_results.csv"
FIGURES_DIR = "legs/leg1_estimation/figures"

ESTIMATORS = {
    "physics_uncalibrated": ("physics_predicted_msun", "physics_pct_error", "Physics (C fixed)"),
    "physics_calibrated": ("physics_calibrated_predicted_msun", "physics_calibrated_pct_error", "Physics (C fit, LOO)"),
    "statistical": ("statistical_predicted_msun", "statistical_pct_error", "Statistical (distance only)"),
}


def load_rows():
    with open(INPUT_CSV, newline="") as f:
        return list(csv.DictReader(f))


def scatter_plot(rows, pred_col, label):
    true_vals = [float(r["reference_msun"]) for r in rows]
    pred_vals = [float(r[pred_col]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(true_vals, pred_vals, alpha=0.6, edgecolors="none")

    lo, hi = 0, max(true_vals + pred_vals) * 1.05
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1, label="y = x (perfect estimate)")

    ax.set_xlabel("Reference chirp mass (M$_\\odot$)")
    ax.set_ylabel("Estimated chirp mass (M$_\\odot$)")
    ax.set_title(f"{label}: estimated vs. reference")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.legend()
    fig.tight_layout()
    return fig


def residual_plot(rows, pred_col, label):
    pred_vals = [float(r[pred_col]) for r in rows]
    residuals = [float(r[pred_col]) - float(r["reference_msun"]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(pred_vals, residuals, alpha=0.6, edgecolors="none")
    ax.axhline(0, color="k", linestyle="--", linewidth=1)

    ax.set_xlabel("Predicted chirp mass (M$_\\odot$)")
    ax.set_ylabel("Residual: predicted $-$ true (M$_\\odot$)")
    ax.set_title(f"{label}: residuals vs. predicted value")
    fig.tight_layout()
    return fig


def error_histogram(rows, err_col, label):
    errors = [float(r[err_col]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.hist(errors, bins=20, edgecolor="black", alpha=0.75)
    ax.axvline(25, color="red", linestyle="--", linewidth=1, label="25% error")

    ax.set_xlabel("Percent error")
    ax.set_ylabel("Number of events")
    ax.set_title(f"{label}: error distribution")
    ax.legend()
    fig.tight_layout()
    return fig


def error_vs_distance_plot(rows, err_col, label):
    distances = [float(r["luminosity_distance_mpc"]) for r in rows]
    errors = [float(r[err_col]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(distances, errors, alpha=0.6, edgecolors="none")
    ax.axhline(25, color="red", linestyle="--", linewidth=1, label="25% error")

    ax.set_xlabel("Luminosity distance (Mpc)")
    ax.set_ylabel("Percent error")
    ax.set_xscale("log")
    ax.set_title(f"{label}: error vs. distance")
    ax.legend()
    fig.tight_layout()
    return fig


def main():
    import os
    os.makedirs(FIGURES_DIR, exist_ok=True)
    rows = load_rows()
    print(f"Loaded {len(rows)} events from {INPUT_CSV}")

    for key, (pred_col, err_col, label) in ESTIMATORS.items():
        for name, fig in [
            ("scatter", scatter_plot(rows, pred_col, label)),
            ("residual", residual_plot(rows, pred_col, label)),
            ("histogram", error_histogram(rows, err_col, label)),
            ("vs_distance", error_vs_distance_plot(rows, err_col, label)),
        ]:
            out_path = f"{FIGURES_DIR}/{key}_{name}.png"
            fig.savefig(out_path, dpi=150)
            plt.close(fig)
            print("saved", out_path)


if __name__ == "__main__":
    main()
