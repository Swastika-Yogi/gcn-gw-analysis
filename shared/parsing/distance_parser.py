"""Extract luminosity distance (with uncertainty, where reported) from circular text."""
import re

# e.g. "luminosity distance estimate is 278 +/- 68 Mpc"
DISTANCE_WITH_ERR_RE = re.compile(
    r"(distance)[^0-9]{0,100}([0-9]+\.?[0-9]*)\s*(?:\+/-|±)\s*([0-9]+\.?[0-9]*)",
    re.IGNORECASE,
)
DISTANCE_RE = re.compile(r"(distance)[^0-9]{0,100}([0-9]+\.?[0-9]*)", re.IGNORECASE)


def extract_distance(text, low=1, high=10000):
    results = []
    covered = set()

    for match in DISTANCE_WITH_ERR_RE.finditer(text):
        try:
            val = float(match.group(2))
            err = float(match.group(3))
        except ValueError:
            continue
        if low < val < high:
            results.append({
                "value": val,
                "lower": val - err,
                "upper": val + err,
                "source_text": match.group(0),
                "confidence": "high",
            })
            covered.add(match.span())

    for match in DISTANCE_RE.finditer(text):
        if any(match.start() >= s and match.start() < e for s, e in covered):
            continue
        try:
            val = float(match.group(2))
        except ValueError:
            continue
        if low < val < high:
            results.append({
                "value": val,
                "lower": None,
                "upper": None,
                "source_text": match.group(0),
                "confidence": "medium",
            })

    return results
