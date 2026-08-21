"""Build the event-level table (section 11 schema) with per-value provenance.

Design choices, made explicit per project-context section 12:
- Multiple circulars can report the same field; when they disagree we keep
  the highest-confidence extraction and log the rest in provenance rather
  than silently averaging or overwriting.
- Missingness is preserved (None), never filled with a guessed default.
- reference_chirp_mass frame is left "unspecified" rather than assumed,
  since the LVK bin sentence doesn't state detector- vs source-frame
  (project context section 9.4).
"""
from shared.ingestion.load_gcn_archive import circular_text
from shared.parsing import classification_parser, distance_parser, far_parser, mass_parser, snr_parser

CONFIDENCE_RANK = {"high": 2, "medium": 1, "low": 0}


def _best(candidates):
    """Pick the highest-confidence candidate dict, or None."""
    if not candidates:
        return None
    return max(candidates, key=lambda c: CONFIDENCE_RANK.get(c.get("confidence"), 0))


def build_event_table(event_to_circulars):
    """event_to_circulars: {event_id: [(file, data), ...]}

    Returns (rows, provenance_log):
      rows - list of dicts matching the section-11 schema (subset implemented so far)
      provenance_log - list of {event_id, field, value, source_circular_id, source_text, parser, confidence}
    """
    rows = []
    provenance_log = []

    for event_id, circulars in event_to_circulars.items():
        distance_candidates = []
        far_candidates = []
        mass_bin_candidates = []
        classification = None
        circular_ids = []
        notes = []

        for file, data in circulars:
            text = circular_text(data)
            circular_id = data.get("circularId", file)
            circular_ids.append(circular_id)

            for c in distance_parser.extract_distance(text):
                c["_circular_id"] = circular_id
                distance_candidates.append(c)

            for c in far_parser.extract_far(text):
                c["_circular_id"] = circular_id
                far_candidates.append(c)

            for c in mass_parser.extract_chirp_mass_bin(text):
                c["_circular_id"] = circular_id
                mass_bin_candidates.append(c)

            cls = classification_parser.extract_classification(text)
            if cls and classification is None:
                classification = cls
                classification["_circular_id"] = circular_id

        best_distance = _best(distance_candidates)
        best_far = _best(far_candidates)
        best_mass_bin = _best(mass_bin_candidates)

        data_quality_flags = []
        if not mass_bin_candidates:
            data_quality_flags.append("no_reference_chirp_mass")
        if not distance_candidates:
            data_quality_flags.append("no_distance")
        if not far_candidates:
            data_quality_flags.append("no_far")

        row = {
            "event_id": event_id,
            "circular_ids": circular_ids,
            "n_circulars": len(circulars),
            "luminosity_distance_mpc": best_distance["value"] if best_distance else None,
            "luminosity_distance_lower_mpc": best_distance.get("lower") if best_distance else None,
            "luminosity_distance_upper_mpc": best_distance.get("upper") if best_distance else None,
            "far_value": best_far["value"] if best_far else None,
            "far_unit": best_far.get("unit") if best_far else None,
            "snr": snr_parser.extract_snr(""),
            "snr_source": "missing",
            "p_bbh": classification["p_bbh"] if classification else None,
            "p_bns": classification["p_bns"] if classification else None,
            "p_nsbh": classification["p_nsbh"] if classification else None,
            "p_terrestrial": classification["p_terrestrial"] if classification else None,
            "source_class": classification["source_class"] if classification else None,
            "reference_chirp_mass": best_mass_bin["mid"] if best_mass_bin else None,
            "reference_chirp_mass_low": best_mass_bin["low"] if best_mass_bin else None,
            "reference_chirp_mass_high": best_mass_bin["high"] if best_mass_bin else None,
            "reference_mass_frame": "unspecified" if best_mass_bin else None,
            "data_quality_flags": ";".join(data_quality_flags),
        }
        rows.append(row)

        for field, best in (
            ("luminosity_distance_mpc", best_distance),
            ("far_value", best_far),
            ("reference_chirp_mass", best_mass_bin),
        ):
            if best:
                provenance_log.append({
                    "event_id": event_id,
                    "field": field,
                    "value": best.get("value", best.get("mid")),
                    "source_circular_id": best.get("_circular_id"),
                    "source_text": best.get("source_text"),
                    "confidence": best.get("confidence"),
                })

    return rows, provenance_log
