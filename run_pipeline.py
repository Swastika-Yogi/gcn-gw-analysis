"""End-to-end O4a pipeline: ingest -> filter -> group -> parse -> event table -> report.

Modeling (chirp-mass estimation) is applied per-event on demand via
src/modeling/chirp_mass_estimator.py rather than baked into this script,
since it depends on assumptions (SNR range, orientation) that should stay
explicit and inspectable rather than hidden in a batch run.
"""
import csv

from src.analysis.reports import data_availability_report, print_report
from src.ingestion.load_gcn_archive import download_and_extract, load_circulars
from src.modeling.apply_estimator import add_chirp_mass_estimates
from src.processing.build_event_table import build_event_table
from src.processing.group_by_event import RUN_WINDOWS, filter_gw_circulars, group_by_event

OUTPUT_CSV = "data/processed/o4a_event_table.csv"


def _mark_missing_as_na(rows):
    """Replace unextracted (None) fields with the literal 'N/A'. Does not
    touch empty-but-valid values like an empty data_quality_flags string,
    which legitimately means 'no flags raised', not 'missing data'."""
    for row in rows:
        for key, value in row.items():
            if value is None:
                row[key] = "N/A"
    return rows


def main():
    folder_path = download_and_extract()
    circulars = load_circulars(folder_path)
    print("Total circulars loaded:", len(circulars))

    gw_circulars = filter_gw_circulars(circulars)
    print("GW-related circulars:", len(gw_circulars))

    run_start, run_end = RUN_WINDOWS["O4a"]
    event_to_circulars = group_by_event(gw_circulars, run_start, run_end)
    print("O4a events found:", len(event_to_circulars))

    rows, provenance_log = build_event_table(event_to_circulars)
    print("Provenance entries logged:", len(provenance_log))

    report = data_availability_report(rows)
    print_report(report, label="O4a")

    add_chirp_mass_estimates(rows)
    estimated = sum(1 for r in rows if r["estimated_chirp_mass_msun"] != "N/A")
    print(f"\nChirp mass estimated for {estimated}/{len(rows)} events (assumed snr/orientation/C - see estimation_notes)")

    _mark_missing_as_na(rows)

    if rows:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print("\nEvent table saved to:", OUTPUT_CSV)

    return rows, provenance_log, report


if __name__ == "__main__":
    main()
