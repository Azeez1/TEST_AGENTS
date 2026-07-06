"""Entity-name normalization so the same business matches across sources.

FROZEN INTERFACE:
    normalize_name(name) -> str
    entity_key(name, zip_code) -> str        # "biz:{name_norm}|{zip5}"
    clean_zip(z) -> str                      # 5-digit zip or ""
"""
import re

# Legal suffixes stripped from the END of names (repeatedly, so
# "ACME TRUCKING CO LLC" -> "ACME TRUCKING"). Multi-word first.
_SUFFIXES = [
    "L L C", "L.L.C.", "L.L.C", "LLC", "L C",
    "INCORPORATED", "INC.", "INC",
    "L.P.", "L P", "LP",
    "LTD.", "LTD",
    "CORPORATION", "CORP.", "CORP",
    "COMPANY", "CO.", "CO",
    "ENTERPRISES", "HOLDINGS",
]

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize_name(name):
    """Uppercase, strip punctuation, collapse whitespace, drop leading THE,
    strip trailing legal suffixes (LLC/INC/LP/LTD/CORP/CO/COMPANY/ENTERPRISES/HOLDINGS).
    """
    if not name:
        return ""
    s = str(name).upper()
    s = _PUNCT_RE.sub(" ", s)          # punctuation -> space (handles "L.L.C." -> "L L C")
    s = _WS_RE.sub(" ", s).strip()
    if s.startswith("THE "):
        s = s[4:]
    changed = True
    while changed and s:
        changed = False
        for suf in _SUFFIXES:
            suf_clean = _WS_RE.sub(" ", _PUNCT_RE.sub(" ", suf)).strip()
            if not suf_clean:
                continue
            if s == suf_clean:
                # name is nothing but a suffix; keep as-is to avoid empty key
                continue
            if s.endswith(" " + suf_clean):
                s = s[: -(len(suf_clean) + 1)].rstrip()
                changed = True
                break
    return s


def clean_zip(z):
    """Return the 5-digit zip from any zip-ish input, or ''."""
    if z is None:
        return ""
    m = re.search(r"\d{5}", str(z))
    return m.group(0) if m else ""


def entity_key(name, zip_code):
    """Canonical business key: 'biz:{name_norm_lower}|{zip5}'."""
    return f"biz:{normalize_name(name).lower()}|{clean_zip(zip_code)}"
