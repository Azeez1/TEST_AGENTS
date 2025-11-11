from typing import List, Dict

# Replace with DB/storage later
_CASES = []
_BIOS = []
_CERTS = []  # e.g., {"type":"SOC2","scope":"Type I","date":"2025-09-01","doc":"...pdf"}

def get(filters: Dict) -> Dict[str, List[Dict]]:
    def _f(coll):
        out = []
        for x in coll:
            ok = all(str(x.get(k,"")).lower().find(str(v).lower())>=0 for k,v in filters.items())
            if ok: out.append(x)
        return out
    return {"case_studies": _f(_CASES), "bios": _f(_BIOS), "certs": _f(_CERTS)}
