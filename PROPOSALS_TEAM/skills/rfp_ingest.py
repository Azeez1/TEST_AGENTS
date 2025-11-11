from typing import Dict, Any
from PyPDF2 import PdfReader

def read(file_path: str) -> Dict[str, Any]:
    reader = PdfReader(file_path)
    pages = [p.extract_text() or "" for p in reader.pages]
    full = "\n".join(pages)

    # naive splits – improve later with rules for "Section L/M"
    instructions = full  # keep entire text; planner will subset
    eval_factors = ""

    return {
        "sections": pages,
        "instructions": instructions,
        "eval_factors": eval_factors,
        "page_map": {i+1: len(pages[i]) for i in range(len(pages))}
    }
