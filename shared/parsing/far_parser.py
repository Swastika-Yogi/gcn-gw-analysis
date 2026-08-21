"""Extract false alarm rate (FAR) from circular text.

FAR is a detection-significance indicator, not SNR - see project context
section 9.1. It should never be silently substituted for SNR upstream.
"""
import re

FAR_RE = re.compile(
    r"(false alarm rate|far)[^0-9]{0,100}([0-9]+\.?[0-9]*e?-?[0-9]*)\s*(hz|/yr|per year)?",
    re.IGNORECASE,
)


def extract_far(text, max_value=1e-2):
    results = []
    for match in FAR_RE.finditer(text):
        try:
            val = float(match.group(2))
        except ValueError:
            continue
        if val >= max_value:
            continue
        unit = (match.group(3) or "").lower() or None
        if unit == "hz":
            unit = "Hz"
        results.append({
            "value": val,
            "unit": unit,
            "source_text": match.group(0),
            "confidence": "high" if unit else "medium",
        })
    return results
