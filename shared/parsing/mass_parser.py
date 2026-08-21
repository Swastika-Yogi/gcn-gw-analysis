"""Extract chirp-mass information from circular text.

Two extraction strategies, in order of trust:

1. `extract_chirp_mass_bin` - the standard LVK identification-circular
   sentence: "The source chirp mass falls with highest probability in the
   bin (22.0, 44.0) solar masses". High confidence: this is exactly the
   quantity we want, reported directly.
2. `extract_mass_generic` - any other number found near the word "mass" /
   "mchirp". Low confidence: this frequently matches unrelated quantities
   (e.g. HasMassGap probabilities), so callers should not average it in
   uncritically alongside bin values.
"""
import re

BIN_RE = re.compile(
    r"chirp mass falls.{0,80}?bin\s*\(([0-9.]+),\s*([0-9.]+)\)", re.IGNORECASE
)
GENERIC_RE = re.compile(r"(mass|mchirp)[^0-9]{0,100}([0-9]+\.?[0-9]*)", re.IGNORECASE)


def extract_chirp_mass_bin(text):
    results = []
    for match in BIN_RE.finditer(text):
        low, high = match.groups()
        try:
            low, high = float(low), float(high)
        except ValueError:
            continue
        results.append({
            "low": low,
            "high": high,
            "mid": (low + high) / 2,
            "source_text": match.group(0),
            "confidence": "high",
        })
    return results


def extract_mass_generic(text, low=1, high=200):
    results = []
    for match in GENERIC_RE.finditer(text):
        try:
            val = float(match.group(2))
        except ValueError:
            continue
        if low < val < high:
            results.append({
                "value": val,
                "source_text": match.group(0),
                "confidence": "low",
            })
    return results
