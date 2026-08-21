"""Extract source-classification probabilities from circular text.

e.g. "classification of the GW signal ... is NSBH (49%), BBH (48%),
Terrestrial (3%), or BNS (<1%)" -> {"NSBH": 49.0, "BBH": 48.0,
"Terrestrial": 3.0, "BNS": 1.0}
"""
import re

CLASS_PAIR_RE = re.compile(r"\b(BBH|BNS|NSBH|Terrestrial)\s*\([<>]?\s*([0-9.]+)\s*%\)", re.IGNORECASE)

LABELS = ("BBH", "BNS", "NSBH", "Terrestrial")
CANONICAL = {label.upper(): label for label in LABELS}


def extract_classification(text):
    """Returns a dict with keys p_bbh, p_bns, p_nsbh, p_terrestrial and
    source_class (the highest-probability label), or None if nothing found."""
    matches = CLASS_PAIR_RE.findall(text)
    if not matches:
        return None

    probs = {label: None for label in LABELS}
    for label, pct in matches:
        label = CANONICAL[label.upper()]
        try:
            probs[label] = float(pct)
        except ValueError:
            continue

    source_class = max(
        (label for label in LABELS if probs[label] is not None),
        key=lambda label: probs[label],
        default=None,
    )

    return {
        "p_bbh": probs["BBH"],
        "p_bns": probs["BNS"],
        "p_nsbh": probs["NSBH"],
        "p_terrestrial": probs["Terrestrial"],
        "source_class": source_class,
    }
