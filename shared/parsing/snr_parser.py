"""GW network SNR extraction.

Deliberately a no-op. "SNR" appears throughout GCN circulars, but almost
always for an instrument's own detection significance (X-ray/optical
follow-up SNR in some energy band), not the LVK trigger's network SNR -
see project context section 9.1 ("FAR is not SNR"; do not infer SNR from
other text without a defensible mapping). Every event is therefore
snr_source="missing" until a genuine, unambiguous source is identified.
"""


def extract_snr(text):
    return None
