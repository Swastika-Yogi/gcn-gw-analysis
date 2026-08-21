"""Group circulars by LVK superevent ID, optionally restricted to a run window."""
from shared.ingestion.load_gcn_archive import circular_text
from shared.parsing.event_id_parser import extract_event_ids, is_gw_related


def filter_gw_circulars(circulars):
    """circulars: list of (file, data). Returns only those mentioning LIGO/Virgo/KAGRA."""
    return [(file, data) for file, data in circulars if is_gw_related(circular_text(data))]


def in_run_window(event_id, start, end):
    """start/end are 6-digit YYMMDD ints (inclusive), matching the S<date><letter> ID scheme."""
    try:
        date_num = int(event_id[1:7])
    except ValueError:
        return False
    return start <= date_num <= end


def group_by_event(gw_circulars, run_start=None, run_end=None):
    """Returns {event_id: [(file, data), ...]}.

    If run_start/run_end are given (YYMMDD ints), only events whose ID falls
    in that inclusive window are kept - e.g. O4a is (230524, 240116).
    """
    event_to_circulars = {}

    for file, data in gw_circulars:
        for event_id in set(extract_event_ids(circular_text(data))):
            if run_start is not None and not in_run_window(event_id, run_start, run_end):
                continue
            event_to_circulars.setdefault(event_id, []).append((file, data))

    return event_to_circulars


# Named run windows, YYMMDD inclusive. Extend as needed.
RUN_WINDOWS = {
    "O4a": (230524, 240116),
}
