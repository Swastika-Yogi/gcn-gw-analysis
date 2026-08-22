"""Validate against the real GWTC catalog (real chirp mass, real SNR),
rather than only the 49 circular-self-reported events.

This is the first point in the project where the physics formula can be
tested with real network SNR instead of an assumed constant - see
legs/leg1_estimation/docs/feasibility_draft.md for why that assumption was
previously the dominant, unresolved error source.

Run from the repo root: python3 -m legs.leg1_estimation.validate_against_catalog
"""
import csv
import math

from shared.ingestion.load_gcn_archive import download_and_extract, load_circulars
from shared.processing.build_event_table import build_event_table
from shared.processing.group_by_event import filter_gw_circulars, group_by_event
from legs.leg1_estimation.modeling.chirp_mass_estimator import estimate_chirp_mass, orientation_factor
from legs.leg1_estimation.validation.load_reference_catalog import (
    download_and_cache,
    download_and_enrich_with_gracedb_id,
    load_catalog_events,
)
from legs.leg1_estimation.validation.match_events import match_catalog_to_circulars
from legs.leg1_estimation.validation.metrics import percent_error, summarize

OUTPUT_CSV = "legs/leg1_estimation/data/processed/catalog_validation_results.csv"
ASSUMED_SNR = 15
ASSUMED_COS_IOTA = 0.5
FALLBACK_C = 1e-4  # only used where we don't refit; kept for comparability with the memo


def fit_c(rows, snr_key):
    """Closed-form C fit (see modeling/calibration.py) but using per-event
    real SNR (snr_key) instead of holding SNR fixed."""
    f_iota = orientation_factor(ASSUMED_COS_IOTA)
    log_c_values = []
    for r in rows:
        x = (r[snr_key] * r["luminosity_distance_mpc"]) / f_iota
        log_c_values.append(math.log(r["chirp_mass_source"]) - 1.2 * math.log(x))
    return math.exp(sum(log_c_values) / len(log_c_values))


def loo_predict(rows, snr_key, c_fitter):
    n = len(rows)
    results = []
    for i in range(n):
        train = rows[:i] + rows[i + 1:]
        c = c_fitter(train, snr_key)
        r = rows[i]
        f_iota = orientation_factor(ASSUMED_COS_IOTA)
        predicted = c * ((r[snr_key] * r["luminosity_distance_mpc"]) / f_iota) ** 1.2
        true = r["chirp_mass_source"]
        results.append({
            "event_id": r["event_id"],
            "predicted_msun": round(predicted, 3),
            "reference_msun": round(true, 3),
            "percent_error": round(percent_error(predicted, true), 1),
            "bin_hit": False,  # catalog chirp mass is continuous, no bin to hit
        })
    return results


def main():
    folder_path = download_and_extract()
    circulars = load_circulars(folder_path)
    gw_circulars = filter_gw_circulars(circulars)
    event_to_circulars = group_by_event(gw_circulars)  # all runs
    rows, _ = build_event_table(event_to_circulars)
    rows_by_id = {r["event_id"]: r for r in rows}

    catalog_path = download_and_cache()
    enriched = download_and_enrich_with_gracedb_id(catalog_path)
    catalog_events = load_catalog_events(enriched)
    print(f"Catalog events (all GWTC releases, deduplicated): {len(catalog_events)}")

    matched, missing, out_of_scope = match_catalog_to_circulars(catalog_events, event_to_circulars)
    print(f"  matched to >=1 circular:        {len(matched)}")
    print(f"  S-id events with NO circular:    {len(missing)}")
    print(f"  pre-2019 (G-id, out of scope):   {len(out_of_scope)}")

    if missing:
        print("\n  Missing events (catalog has them, our circular archive doesn't):")
        for e in missing[:15]:
            print(f"    {e['gracedb_id']} ({e['common_name']}, {e['catalog']})")
        if len(missing) > 15:
            print(f"    ... and {len(missing) - 15} more")

    # Build the combined validation set: circular-extracted distance +
    # catalog-provided true chirp mass and real SNR.
    combined = []
    for cat_event in matched:
        circ_row = rows_by_id[cat_event["gracedb_id"]]
        if circ_row["luminosity_distance_mpc"] is None:
            continue
        if cat_event["chirp_mass_source"] is None:
            continue
        if cat_event["network_matched_filter_snr"] is None:
            continue
        combined.append({
            "event_id": cat_event["gracedb_id"],
            "luminosity_distance_mpc": circ_row["luminosity_distance_mpc"],  # from OUR circular extraction
            "catalog_distance_mpc": cat_event["luminosity_distance"],        # catalog's own distance, for comparison
            "chirp_mass_source": cat_event["chirp_mass_source"],
            "real_snr": cat_event["network_matched_filter_snr"],
            "source_class": circ_row["source_class"],
        })

    print(f"\nCombined validation set (circular distance + catalog mass/SNR): {len(combined)} events")
    if not combined:
        print("No usable combined events - stopping.")
        return

    for r in combined:
        r["assumed_snr"] = ASSUMED_SNR

    real_results = loo_predict(combined, "real_snr", fit_c)
    print()
    hits, n = summarize(real_results)["within_25pct"]
    s = summarize(real_results)
    print(f"Physics, REAL SNR, C fit per-fold (LOO):    median={s['median_percent_error']:>6.1f}%  within25={hits:>2}/{n}  MAE={s['mae_msun']:.2f} Msun  bias={s['bias_msun']:+.2f} Msun")

    assumed_results = loo_predict(combined, "assumed_snr", fit_c)
    s2 = summarize(assumed_results)
    hits2, n2 = s2["within_25pct"]
    print(f"Physics, ASSUMED SNR={ASSUMED_SNR}, C fit per-fold (LOO): median={s2['median_percent_error']:>6.1f}%  within25={hits2:>2}/{n2}  MAE={s2['mae_msun']:.2f} Msun  bias={s2['bias_msun']:+.2f} Msun")

    with open(OUTPUT_CSV, "w", newline="") as f:
        fieldnames = ["event_id", "source_class", "circular_distance_mpc", "catalog_distance_mpc",
                      "real_snr", "chirp_mass_source",
                      "real_snr_predicted_msun", "real_snr_pct_error",
                      "assumed_snr_predicted_msun", "assumed_snr_pct_error"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c, real, assumed in zip(combined, real_results, assumed_results):
            writer.writerow({
                "event_id": c["event_id"],
                "source_class": c["source_class"],
                "circular_distance_mpc": c["luminosity_distance_mpc"],
                "catalog_distance_mpc": c["catalog_distance_mpc"],
                "real_snr": c["real_snr"],
                "chirp_mass_source": c["chirp_mass_source"],
                "real_snr_predicted_msun": real["predicted_msun"],
                "real_snr_pct_error": real["percent_error"],
                "assumed_snr_predicted_msun": assumed["predicted_msun"],
                "assumed_snr_pct_error": assumed["percent_error"],
            })
    print("\nPer-event results saved to:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
