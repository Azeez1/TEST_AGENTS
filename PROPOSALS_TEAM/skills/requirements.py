import re
from typing import List, Dict

REQ_PAT = re.compile(r'(?P<id>[A-Z][\w\.-]{0,8}[\.\-]?\d{0,3})?[^.\n]*\b(shall|must|will)\b[^.\n]*\.', re.IGNORECASE)

def extract(rfp_text: str) -> List[Dict]:
    rows = []
    for i, m in enumerate(REQ_PAT.finditer(rfp_text), start=1):
        verb = m.group(0).strip()
        rows.append({
            "req_id": f"REQ-{i:04d}",
            "verbatim": verb,
            "must_or_should": "must" if re.search(r'\b(shall|must)\b', verb, re.I) else "should",
            "section": None,
            "eval_factor": None
        })
    return rows
