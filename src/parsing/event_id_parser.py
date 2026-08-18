"""Extract LVK superevent IDs (e.g. S230627c, S251116en) from circular text."""
import re

# Superevent IDs are "S" + 6-digit date + a base-26 letter suffix (a, b, ..., z,
# aa, ab, ...). Once a day's single-letter suffixes are exhausted the suffix
# grows to two (and, rarely, three) lowercase letters, so a single [a-z] here
# silently drops every event from a busy observing period.
EVENT_ID_RE = re.compile(r"S\d{6}[a-z]{1,3}\b")


def extract_event_ids(text):
    """All superevent IDs mentioned in a piece of text, in order of appearance."""
    return EVENT_ID_RE.findall(text)


def is_gw_related(text):
    """Cheap keyword screen for whether a circular concerns a GW event."""
    lowered = text.lower()
    return any(k in lowered for k in ("ligo", "virgo", "kagra"))
