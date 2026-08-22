"""Step 1: validate the FAR->SNR proxy on its own (does it predict real SNR
well?), before using it anywhere downstream.

Run: python3 -m legs.leg1_estimation.validate_far_snr_proxy
"""
import json
import math

from legs.leg1_estimation.modeling.far_snr_proxy import fit_proxy, predict_snr
from legs.leg1_estimation.validation.load_reference_catalog import ENRICHED_CACHE_PATH


def load_far_snr_pairs():
    with open(ENRICHED_CACHE_PATH) as f:
        enriched = json.load(f)
    pairs = []
    for name, v in enriched.items():
        snr = v.get("network_matched_filter_snr")
        far = v.get("far")
        if snr is not None and far is not None and far > 0:
            pairs.append({"name": name, "snr": snr, "far": far})
    return pairs


def loo_validate(pairs):
    n = len(pairs)
    results = []
    for i in range(n):
        train = pairs[:i] + pairs[i + 1:]
        coef = fit_proxy([p["far"] for p in train], [p["snr"] for p in train])
        true_snr = pairs[i]["snr"]
        pred_snr = predict_snr(coef, pairs[i]["far"])
        err_pct = abs(pred_snr - true_snr) / true_snr * 100
        results.append({"name": pairs[i]["name"], "true_snr": true_snr, "pred_snr": pred_snr, "pct_error": err_pct})
    return results


def main():
    pairs = load_far_snr_pairs()
    print(f"Real (SNR, FAR) pairs: {len(pairs)}")

    all_results = loo_validate(pairs)
    non_floor = [p for p in pairs if p["far"] != 1e-05]
    print(f"  excluding {len(pairs) - len(non_floor)} events at the FAR floor (1e-5/yr): {len(non_floor)} remain")
    non_floor_results = loo_validate(non_floor)

    for label, results in [("All events (incl. FAR floor)", all_results), ("Excluding FAR-floor events", non_floor_results)]:
        errors = sorted(r["pct_error"] for r in results)
        n = len(errors)
        within25 = sum(1 for e in errors if e <= 25)
        within50 = sum(1 for e in errors if e <= 50)
        print(f"{label}: median={errors[n//2]:.1f}%  within25={within25}/{n}  within50={within50}/{n}  max={errors[-1]:.1f}%")

    # fit on the full set for downstream use
    coef = fit_proxy([p["far"] for p in pairs], [p["snr"] for p in pairs])
    print(f"\nFull-data fit: log(SNR) = {coef[0]:.3f} + {coef[1]:.3f} * log(FAR)")


if __name__ == "__main__":
    main()
