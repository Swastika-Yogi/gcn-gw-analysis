"""M5.1 — Availability analysis.

For each of the four extractable fields (distance, FAR, classification,
reference chirp mass), report:
  - overall count/percentage across every S-ID event in the archive
  - breakdown by named observing run
  - breakdown by source class (BBH/NSBH/BNS/Terrestrial)
  - breakdown by circular type (identification/update/retraction/external
    follow-up), computed per-circular rather than per-event, since "which
    circular type actually carries this field" is a per-circular question
  - typical uncertainty when reported (distance ± bounds, chirp-mass bin
    width; FAR and classification are point/probability values, not
    reported with an uncertainty, so are marked not-applicable rather than
    silently given a fabricated number)

Run as: python3 -m legs.leg1_estimation.analysis.availability_analysis
"""
import re
import statistics

from shared.ingestion.load_gcn_archive import download_and_extract, load_circulars, circular_text
from shared.parsing import classification_parser, distance_parser, far_parser, mass_parser
from shared.processing.group_by_event import filter_gw_circulars, group_by_event, in_run_window, RUN_WINDOWS
from shared.processing.build_event_table import build_event_table

FIELDS = ["luminosity_distance_mpc", "far_value", "source_class", "reference_chirp_mass"]
FIELD_LABELS = {
    "luminosity_distance_mpc": "Distance",
    "far_value": "FAR",
    "source_class": "Classification",
    "reference_chirp_mass": "Chirp mass",
}

LVK_PREFIX_RE = re.compile(r"^\s*LIGO[/-]?Virgo", re.IGNORECASE)
RETRACTION_RE = re.compile(r"retraction", re.IGNORECASE)
IDENTIFICATION_RE = re.compile(r"identification of a gw", re.IGNORECASE)
UPDATE_RE = re.compile(r"\bupdate", re.IGNORECASE)


def classify_circular_type(subject):
    if not LVK_PREFIX_RE.match(subject):
        return "external_followup"
    if RETRACTION_RE.search(subject):
        return "retraction"
    if IDENTIFICATION_RE.search(subject):
        return "identification"
    if UPDATE_RE.search(subject):
        return "update"
    return "lvk_other"


def event_run(event_id):
    date_num = int(event_id[1:7])
    for run, (start, end) in RUN_WINDOWS.items():
        if in_run_window(event_id, start, end):
            return run
    return "unclassified_gap"


def pct(n, total):
    return f"{n}/{total} ({100 * n / total:.1f}%)" if total else "0/0 (n/a)"


def overall_and_by_run(rows):
    total = len(rows)
    print(f"\n=== Overall coverage ({total} events, all S-ID runs) ===")
    for field in FIELDS:
        n = sum(1 for r in rows if r[field] is not None)
        print(f"{FIELD_LABELS[field]:14s} {pct(n, total)}")

    runs_present = [r for r in RUN_WINDOWS if any(r == row["_run"] for row in rows)]
    print(f"\n=== Coverage by observing run ===")
    header = f"{'Run':10s}" + "".join(f"{FIELD_LABELS[f]:>16s}" for f in FIELDS) + "   n"
    print(header)
    for run in list(RUN_WINDOWS) + ["unclassified_gap"]:
        run_rows = [r for r in rows if r["_run"] == run]
        if not run_rows:
            continue
        line = f"{run:10s}"
        for field in FIELDS:
            n = sum(1 for r in run_rows if r[field] is not None)
            line += f"{pct(n, len(run_rows)):>16s}"
        line += f"   {len(run_rows)}"
        print(line)


def by_source_class(rows):
    print(f"\n=== Coverage by source class (among events with a classification) ===")
    classified = [r for r in rows if r["source_class"] is not None]
    classes = sorted(set(r["source_class"] for r in classified))
    other_fields = ["luminosity_distance_mpc", "far_value", "reference_chirp_mass"]
    header = f"{'Class':14s}{'n':>6s}" + "".join(f"{FIELD_LABELS[f]:>20s}" for f in other_fields)
    print(header)
    for cls in classes:
        cls_rows = [r for r in classified if r["source_class"] == cls]
        line = f"{cls:14s}{len(cls_rows):>6d}"
        for field in other_fields:
            n = sum(1 for r in cls_rows if r[field] is not None)
            line += f"{pct(n, len(cls_rows)):>20s}"
        print(line)


def by_circular_type(gw_circulars):
    print(f"\n=== Coverage by circular type (per-circular, not per-event) ===")
    typed = {}
    for file, data in gw_circulars:
        subject = str(data.get("subject", ""))
        ctype = classify_circular_type(subject)
        typed.setdefault(ctype, []).append(data)

    header = f"{'Type':20s}{'n':>8s}" + "".join(f"{FIELD_LABELS[f]:>20s}" for f in FIELDS if f != "reference_chirp_mass") + f"{'Chirp mass':>20s}"
    print(header)
    for ctype, circs in sorted(typed.items(), key=lambda kv: -len(kv[1])):
        n = len(circs)
        n_dist = sum(1 for d in circs if distance_parser.extract_distance(circular_text(d)))
        n_far = sum(1 for d in circs if far_parser.extract_far(circular_text(d)))
        n_class = sum(1 for d in circs if classification_parser.extract_classification(circular_text(d)))
        n_mass = sum(1 for d in circs if mass_parser.extract_chirp_mass_bin(circular_text(d)))
        line = f"{ctype:20s}{n:>8d}{pct(n_dist, n):>20s}{pct(n_far, n):>20s}{pct(n_class, n):>20s}{pct(n_mass, n):>20s}"
        print(line)


def typical_uncertainty(rows):
    print(f"\n=== Typical uncertainty when reported ===")

    dist_rows = [r for r in rows if r["luminosity_distance_mpc"] is not None]
    dist_with_err = [r for r in dist_rows if r["luminosity_distance_lower_mpc"] is not None]
    print(f"Distance: {pct(len(dist_with_err), len(dist_rows))} of distance-bearing events include an explicit +/- bound")
    if dist_with_err:
        rel_widths = [
            100 * (r["luminosity_distance_upper_mpc"] - r["luminosity_distance_lower_mpc"]) / 2 / r["luminosity_distance_mpc"]
            for r in dist_with_err
        ]
        print(f"  median relative half-width: {statistics.median(rel_widths):.1f}%  (n={len(rel_widths)})")

    mass_rows = [r for r in rows if r["reference_chirp_mass"] is not None]
    if mass_rows:
        rel_widths = [
            100 * (r["reference_chirp_mass_high"] - r["reference_chirp_mass_low"]) / 2 / r["reference_chirp_mass"]
            for r in mass_rows
        ]
        print(f"Chirp mass bin: {len(mass_rows)} events, median relative half-width {statistics.median(rel_widths):.1f}% (bin, not a statistical error bar)")

    print("FAR: reported as a single point value, no uncertainty given in circular text -- not applicable")
    print("Classification: reported as point probabilities, no uncertainty given in circular text -- not applicable")


def main():
    download_and_extract()
    circulars = load_circulars()
    gw_circulars = filter_gw_circulars(circulars)
    event_to_circulars = group_by_event(gw_circulars)

    rows, _ = build_event_table(event_to_circulars)
    for row in rows:
        row["_run"] = event_run(row["event_id"])

    overall_and_by_run(rows)
    by_source_class(rows)
    by_circular_type(gw_circulars)
    typical_uncertainty(rows)


if __name__ == "__main__":
    main()
