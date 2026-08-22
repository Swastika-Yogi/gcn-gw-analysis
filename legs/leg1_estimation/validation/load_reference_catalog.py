"""Load the public GWTC catalog from GWOSC as an external reference for
validation - matches the architecture the original project brief proposed
(validation/load_reference_catalog.py) before this was deferred pending the
external-catalog scope question.

Cross-matching to circulars: post-2019 events use the "S..." superevent ID
system, and GWOSC's `gracedb_id` field for those events IS that exact ID
(confirmed directly: GW230627_015337's gracedb_id is "S230627c", matching
the circular event S230627c). Pre-2019 events (O1/O2/O3-era, before
superevents existed) have "G..."-format gracedb_id instead - those can't be
matched against our circular pipeline, which only extracts "S..." IDs, and
are treated as out of scope here rather than guessed at.

Crucially, GWOSC gives real network_matched_filter_snr - the one quantity
that is structurally absent from circular text (see project context
section 9.1, feasibility memo). This is the first point in the project
where the physics estimator can be tested against real SNR instead of an
assumed one.
"""
import json
import os

import requests

CATALOG_URL = "https://gwosc.org/eventapi/json/GWTC/"
CACHE_PATH = "legs/leg1_estimation/data/raw/gwtc_catalog.json"
ENRICHED_CACHE_PATH = "legs/leg1_estimation/data/raw/gwtc_catalog_enriched.json"


def download_and_cache(force=False):
    if os.path.exists(CACHE_PATH) and not force:
        print(f"GWTC catalog already cached at {CACHE_PATH}, skipping download.")
        return CACHE_PATH

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    print("Downloading GWTC catalog from GWOSC...")
    response = requests.get(CATALOG_URL, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download GWTC catalog. Status: {response.status_code}")

    with open(CACHE_PATH, "w") as f:
        f.write(response.text)
    print(f"Saved to {CACHE_PATH}")
    return CACHE_PATH


def download_and_enrich_with_gracedb_id(bulk_path=CACHE_PATH, force=False):
    """The bulk /eventapi/json/GWTC/ listing does not include gracedb_id
    (the field that, for post-2019 events, IS the circular "S..." ID) -
    that only appears on each event's individual detail endpoint. This
    fetches all ~390 of those once and caches the enriched result, since
    re-fetching every run would be slow and unkind to a public API.
    """
    if os.path.exists(ENRICHED_CACHE_PATH) and not force:
        print(f"Enriched GWTC catalog already cached at {ENRICHED_CACHE_PATH}, skipping.")
        with open(ENRICHED_CACHE_PATH) as f:
            return json.load(f)

    with open(bulk_path) as f:
        raw = json.load(f)["events"]

    by_common_name = {}
    for record in raw.values():
        name = record["commonName"]
        if name not in by_common_name or record["version"] > by_common_name[name]["version"]:
            by_common_name[name] = record

    print(f"Fetching gracedb_id for {len(by_common_name)} events (one request each, cached after)...")
    enriched = {}
    for i, (name, record) in enumerate(by_common_name.items()):
        if i % 50 == 0:
            print(f"  {i}/{len(by_common_name)}")
        try:
            detail = requests.get(record["jsonurl"], timeout=15)
            detail_record = list(detail.json()["events"].values())[0]
            record = dict(record)
            record["gracedb_id"] = detail_record.get("gracedb_id")
        except Exception:
            record = dict(record)
            record["gracedb_id"] = None
        enriched[name] = record

    os.makedirs(os.path.dirname(ENRICHED_CACHE_PATH), exist_ok=True)
    with open(ENRICHED_CACHE_PATH, "w") as f:
        json.dump(enriched, f)
    print(f"Saved enriched catalog to {ENRICHED_CACHE_PATH}")
    return enriched


def load_catalog_events(enriched_events=None):
    """Returns a list of catalog event records, one per unique commonName.
    Pass the dict from download_and_enrich_with_gracedb_id() (that's the
    only source with gracedb_id populated; the plain bulk cache doesn't
    have it - see that function's docstring)."""
    if enriched_events is None:
        with open(ENRICHED_CACHE_PATH) as f:
            enriched_events = json.load(f)
    by_common_name = enriched_events

    events = []
    for record in by_common_name.values():
        gracedb_id = record.get("gracedb_id")
        events.append({
            "common_name": record["commonName"],
            "gracedb_id": gracedb_id,
            "is_superevent_id": bool(gracedb_id and gracedb_id.startswith("S")),
            "catalog": record.get("catalog.shortName"),
            "gps_time": record.get("GPS"),
            "chirp_mass_source": record.get("chirp_mass_source"),
            "mass_1_source": record.get("mass_1_source"),
            "mass_2_source": record.get("mass_2_source"),
            "network_matched_filter_snr": record.get("network_matched_filter_snr"),
            "luminosity_distance": record.get("luminosity_distance"),
            "far": record.get("far"),
        })
    return events
