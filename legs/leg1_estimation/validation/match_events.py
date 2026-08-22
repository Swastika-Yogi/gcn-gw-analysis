"""Cross-match GWTC catalog events against our circular-derived event table.

Only catalog events with a superevent-style ("S...") gracedb_id are
matchable at all - older (pre-2019) events use the "G..." GraceDB ID format
from before the superevent system existed, and our circular pipeline only
ever extracts "S..." IDs (see shared/parsing/event_id_parser.py), so those
are structurally out of scope here, not silently mismatched.
"""


def match_catalog_to_circulars(catalog_events, event_to_circulars):
    """Returns (matched, missing, out_of_scope):
    - matched: catalog events whose gracedb_id has at least one circular
    - missing: catalog events with an S-id gracedb_id but NO circular found
    - out_of_scope: catalog events with a non-S-id gracedb_id (pre-2019)
    """
    matched, missing, out_of_scope = [], [], []
    for event in catalog_events:
        if not event["is_superevent_id"]:
            out_of_scope.append(event)
            continue
        if event["gracedb_id"] in event_to_circulars:
            matched.append(event)
        else:
            missing.append(event)
    return matched, missing, out_of_scope
