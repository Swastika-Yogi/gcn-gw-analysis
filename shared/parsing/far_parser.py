"""Extract false alarm rate (FAR) from circular text.

FAR is a detection-significance indicator, not SNR - see project context
section 9.1. It should never be silently substituted for SNR upstream.
"""
import re

# Bare "far" is only trusted as the FAR abbreviation when capitalized (FAR);
# case-insensitive matching on that alternative let ordinary English usage
# ("so far", "as far as", "thus far", each often followed by an unrelated
# nearby number) get misread as a fabricated FAR value - caught during the
# M4.4 extraction audit (docs/feasibility_draft.md Section 4.4/4).
FAR_RE = re.compile(
    r"((?i:false alarm rate)|\bFAR\b)[^0-9]{0,100}([0-9]+\.?[0-9]*e?-?[0-9]*)\s*((?i:hz|/yr|per year))?",
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
