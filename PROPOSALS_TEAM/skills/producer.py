import json
from typing import Dict, Any, List

def package(sections: List[Dict[str, Any]], matrix_csv: str, annexes: List[str]) -> Dict[str, str]:
    # Write files to /out; real PDF assembly can use ReportLab or LibreOffice headless export
    with open("deliverables.json","w") as f:
        json.dump({"sections":[s["title"] for s in sections],
                   "matrix":"compliance_matrix.csv",
                   "annexes":annexes}, f, indent=2)
    with open("compliance_matrix.csv","w") as f:
        f.write(matrix_csv)
    return {"bundle": "deliverables.json", "matrix": "compliance_matrix.csv"}
