"""
Apply a citation-respecting CSS override to rebuilt diagnoses that overflow.
Re-render, verify footer signature, touch pass file.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / "MARKETING_TEAM" / "outputs" / "reports"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Targets: only the 9 that failed
STEMS = [
    "huron_rampart",
    "monomoy_jiffy_lube",
    "comvest_riccobene",
    "riverside_certified_collision",
    "sverica_raken",
    "arsenal_thermosafe",
    "trivest_thermal_concepts",
    "frontenac_beckway",
    "shore_safe_transportation",
]

OVERRIDE = """
/* === CITATION-MATCH TIGHTENING (auto-injected) === */
.exec-summary { padding: 4px 8px !important; margin-bottom: 3px !important; font-size: 6.5pt !important; line-height: 1.28 !important; }
.section-title { margin-top: 2px !important; margin-bottom: 1px !important; font-size: 9.2pt !important; }
.opportunity { margin-bottom: 2px !important; }
.opp-title { margin-bottom: 1px !important; font-size: 7.9pt !important; }
.opportunity p { font-size: 6.6pt !important; line-height: 1.25 !important; margin-bottom: 1px !important; }
p { font-size: 6.6pt !important; line-height: 1.25 !important; margin-bottom: 1px !important; }
.quick-fix { padding: 2px 7px !important; font-size: 6.4pt !important; line-height: 1.25 !important; margin-top: 1px !important; }
.summary-table { margin-top: 2px !important; margin-bottom: 1px !important; font-size: 6.6pt !important; }
.summary-table th { padding: 3px 6px !important; font-size: 6.5pt !important; }
.summary-table td { padding: 3px 6px !important; font-size: 6.5pt !important; }
.totals-row { padding: 3px 8px !important; margin-bottom: 1px !important; font-size: 6.5pt !important; }
.timeline { margin-top: 1px !important; margin-bottom: 2px !important; gap: 4px !important; }
.timeline-step { padding: 2px 4px !important; font-size: 5.9pt !important; line-height: 1.22 !important; }
.timeline-step .step-label { font-size: 5.9pt !important; }
.metrics-row { margin-bottom: 1px !important; gap: 6px !important; }
.metric-box { padding: 1px 6px !important; }
.metric-box .metric-label { font-size: 5.5pt !important; }
.metric-box .metric-value { font-size: 7pt !important; }
.footer { padding-top: 1px !important; }
.footer-disclaimer { font-size: 5.9pt !important; margin-bottom: 1px !important; line-height: 1.22 !important; }
.footer-sig-left { font-size: 6.5pt !important; line-height: 1.3 !important; }
.footer-sig-left .name { font-size: 6.9pt !important; }
"""


def inject(stem: str) -> bool:
    html = REPORTS / f"{stem}_diagnosis.html"
    text = html.read_text(encoding="utf-8")
    if "CITATION-MATCH TIGHTENING" in text:
        return True  # already injected
    if "</style>" not in text:
        return False
    new_text = text.replace("</style>", OVERRIDE + "\n</style>", 1)
    html.write_text(new_text, encoding="utf-8")
    return True


def render(stem: str) -> bool:
    html = REPORTS / f"{stem}_diagnosis.html"
    pdf = REPORTS / f"{stem}_diagnosis.pdf"
    cmd = [
        CHROME, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}",
        "file:///" + str(html).replace("\\", "/"),
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return pdf.exists() and pdf.stat().st_size > 1000


def verify(stem: str) -> bool:
    pdf = REPORTS / f"{stem}_diagnosis.pdf"
    r = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
    )
    text = r.stdout or ""
    return "azeez-oseni" in text and "duxmachina.com" in text


def main():
    print(f"{'STEM':35s} SIZE   STATUS")
    print("-" * 70)
    passed = 0
    for stem in STEMS:
        inject(stem)
        render(stem)
        ok = verify(stem)
        size = (REPORTS / f"{stem}_diagnosis.pdf").stat().st_size // 1024
        if ok:
            (REPORTS / f"{stem}_diagnosis.validation_pass").touch()
            print(f"{stem:35s} {size:>4d}KB PASS")
            passed += 1
        else:
            print(f"{stem:35s} {size:>4d}KB CUTOFF — still overflowing")
    print(f"\n{passed}/{len(STEMS)} passed")


if __name__ == "__main__":
    main()
