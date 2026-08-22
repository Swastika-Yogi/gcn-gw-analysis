"""Step 2: does the FAR->SNR proxy (validated on its own in
validate_far_snr_proxy.py) actually improve the physics formula on the
original 49-event circular-only validation set?

Leakage care: some of these 49 events are also among the 381 catalog
events used to fit the proxy. For each of the 49, the proxy is refit
excluding that event (by gracedb_id) before predicting its SNR, so no
event's own real SNR ever leaks into its own prediction, directly or
through the proxy.

Run: python3 -m legs.leg1_estimation.validate_far_proxy_estimator
"""
import json
import math

from shared.ingestion.load_gcn_archive import download_and_extract, load_circulars
from shared.processing.build_event_table import build_event_table
from shared.processing.group_by_event import filter_gw_circulars, group_by_event
from legs.leg1_estimation.modeling.calibration import fit_c
from legs.leg1_estimation.modeling.chirp_mass_estimator import orientation_factor
from legs.leg1_estimation.modeling.far_snr_proxy import far_hz_to_per_year, fit_proxy, predict_snr
from legs.leg1_estimation.validation.build_validation_set import build_validation_set
from legs.leg1_estimation.validation.load_reference_catalog import ENRICHED_CACHE_PATH
from legs.leg1_estimation.validation.metrics import percent_error, summarize

ASSUMED_COS_IOTA = 0.5


def fit_c_per_row_snr(rows_and_snrs, cos_iota):
    """Same closed-form C fit as modeling/calibration.py, but each row
    carries its OWN SNR (proxy-predicted, not one shared assumed value) -
    rows_and_snrs is a list of (row, snr) pairs."""
    f_iota = orientation_factor(cos_iota)
    log_c_values = []
    for row, snr in rows_and_snrs:
        x = (snr * row["luminosity_distance_mpc"]) / f_iota
        log_c_values.append(math.log(row["reference_chirp_mass"]) - 1.2 * math.log(x))
    return math.exp(sum(log_c_values) / len(log_c_values))


def load_catalog_far_snr_by_gracedb_id():
    with open(ENRICHED_CACHE_PATH) as f:
        enriched = json.load(f)
    out = {}
    for v in enriched.values():
        gid = v.get("gracedb_id")
        snr = v.get("network_matched_filter_snr")
        far = v.get("far")
        if gid and snr is not None and far is not None and far > 0:
            out[gid] = {"snr": snr, "far": far}
    return out


def main():
    folder_path = download_and_extract()
    circulars = load_circulars(folder_path)
    gw_circulars = filter_gw_circulars(circulars)
    event_to_circulars = group_by_event(gw_circulars)
    rows, _ = build_event_table(event_to_circulars)

    val = build_validation_set(rows)  # the same 49-event circular-only set as validate_estimator.py
    print(f"Circular-only validation set: {len(val)} events")

    val_with_far = [r for r in val if r["far_value"] is not None]
    print(f"  ...with circular-extracted FAR: {len(val_with_far)}")

    catalog_pairs = load_catalog_far_snr_by_gracedb_id()
    print(f"Catalog (SNR, FAR) pairs available for proxy fitting: {len(catalog_pairs)}")

    f_iota = orientation_factor(ASSUMED_COS_IOTA)
    results_proxy = []
    results_fixed15 = []

    def proxy_snr_for(row, exclude_gid):
        """FAR->SNR proxy prediction for one row, fit excluding exclude_gid
        (so an event's own real SNR never leaks into its own C-fitting or
        its own final prediction, even indirectly through the proxy)."""
        train_pairs = [(v["far"], v["snr"]) for gid, v in catalog_pairs.items() if gid != exclude_gid]
        coef = fit_proxy([p[0] for p in train_pairs], [p[1] for p in train_pairs])
        return predict_snr(coef, far_hz_to_per_year(row["far_value"]))

    for i, r in enumerate(val_with_far):
        true_mass = r["reference_chirp_mass"]

        # --- proxy branch: this event's own predicted SNR, held out from proxy fitting ---
        predicted_snr = proxy_snr_for(r, exclude_gid=r["event_id"])

        # --- fit C on the other 48 circular-only events, each using ITS OWN
        # proxy-predicted SNR (not one shared value) - restricted to events
        # that have circular FAR, since C-fitting here needs a per-row SNR ---
        train_rows_and_snrs = [
            (x, proxy_snr_for(x, exclude_gid=x["event_id"]))  # each row's own SNR excluded from its own proxy prediction too
            for x in val_with_far if x["event_id"] != r["event_id"]
        ]
        c = fit_c_per_row_snr(train_rows_and_snrs, ASSUMED_COS_IOTA)

        predicted_mass_proxy = c * ((predicted_snr * r["luminosity_distance_mpc"]) / f_iota) ** 1.2
        results_proxy.append({
            "event_id": r["event_id"], "predicted_msun": round(predicted_mass_proxy, 3),
            "reference_msun": round(true_mass, 3),
            "percent_error": round(percent_error(predicted_mass_proxy, true_mass), 1),
            "bin_hit": r["reference_chirp_mass_low"] <= predicted_mass_proxy <= r["reference_chirp_mass_high"],
            "predicted_snr": round(predicted_snr, 2),
        })

        # --- comparison: fixed SNR=15 baseline, same C-fitting procedure, same event subset ---
        train_rows_fixed = [x for x in val_with_far if x["event_id"] != r["event_id"]]
        c15 = fit_c(train_rows_fixed, 15, ASSUMED_COS_IOTA)
        predicted_mass_15 = c15 * ((15 * r["luminosity_distance_mpc"]) / f_iota) ** 1.2
        results_fixed15.append({
            "event_id": r["event_id"], "predicted_msun": round(predicted_mass_15, 3),
            "reference_msun": round(true_mass, 3),
            "percent_error": round(percent_error(predicted_mass_15, true_mass), 1),
            "bin_hit": r["reference_chirp_mass_low"] <= predicted_mass_15 <= r["reference_chirp_mass_high"],
        })

    def report(label, results):
        s = summarize(results)
        hits, n = s["within_25pct"]
        bhits, bn = s["bin_hit_rate"]
        print(f"{label:<45} median={s['median_percent_error']:>6.1f}%  within25={hits:>2}/{n}  bin-hit={bhits:>2}/{bn}  MAE={s['mae_msun']:.2f} Msun")

    print()
    report("Physics, SNR from FAR-proxy, C fit (LOO)", results_proxy)
    report("Physics, fixed SNR=15, C fit (LOO)", results_fixed15)


if __name__ == "__main__":
    main()
