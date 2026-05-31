"""
Batch render the 10 rebuilt diagnosis HTMLs to PDF, verify footer signature,
and refresh validation_pass markers.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / "MARKETING_TEAM" / "outputs" / "reports"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

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
    "align_pentagon_ems",
]


def render(stem: str) -> bool:
    html = REPORTS / f"{stem}_diagnosis.html"
    pdf = REPORTS / f"{stem}_diagnosis.pdf"
    html_url = "file:///" + str(html).replace("\\", "/")
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}",
        html_url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return pdf.exists() and pdf.stat().st_size > 1000


def verify_footer(stem: str) -> tuple[bool, str]:
    pdf = REPORTS / f"{stem}_diagnosis.pdf"
    r = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, timeout=20, encoding="utf-8", errors="replace"
    )
    text = r.stdout or ""
    has_li = "azeez-oseni" in text or "linkedin.com/in" in text
    has_dm = "duxmachina.com" in text
    return (has_li and has_dm), f"li={has_li} dm={has_dm}"


def touch_pass(stem: str):
    p = REPORTS / f"{stem}_diagnosis.validation_pass"
    p.touch()


def main():
    print(f"{'STEM':35s} {'SIZE':>8s}  {'FOOTER':10s}  NOTES")
    print("-" * 90)
    results = []
    for stem in STEMS:
        ok = render(stem)
        if not ok:
            print(f"{stem:35s}    FAIL   render failed")
            results.append((stem, False, "render failed"))
            continue
        size = (REPORTS / f"{stem}_diagnosis.pdf").stat().st_size
        footer_ok, why = verify_footer(stem)
        if footer_ok:
            touch_pass(stem)
            print(f"{stem:35s} {size//1024:>5d} KB  PASS       footer present, pass file refreshed")
        else:
            print(f"{stem:35s} {size//1024:>5d} KB  CUTOFF     {why}")
        results.append((stem, footer_ok, why if not footer_ok else "ok"))

    print()
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"{passed}/{len(STEMS)} passed footer verification")


if __name__ == "__main__":
    main()
