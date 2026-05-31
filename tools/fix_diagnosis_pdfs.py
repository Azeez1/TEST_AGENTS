"""
Fix overflow-cutoff PE diagnosis PDFs by injecting tight CSS overrides
and re-rendering each via Chrome headless.

Usage: python tools/fix_diagnosis_pdfs.py
"""
import subprocess
import sys
import os
from pathlib import Path

REPORTS_DIR = Path("MARKETING_TEAM/outputs/reports")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

TARGETS = [
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

CSS_OVERRIDE = """
/* === BOTTOM-OVERFLOW FIX OVERRIDES (injected by fix_diagnosis_pdfs.py) === */
.page { padding: 0.16in 0.42in 0.10in 0.42in !important; }
.header { margin-bottom: 0.06in !important; padding-bottom: 0.05in !important; }
.header-title { font-size: 13.5pt !important; }
.exec-summary { padding: 3px 8px !important; margin-bottom: 3px !important; font-size: 6.4pt !important; line-height: 1.25 !important; }
.section-title { font-size: 9pt !important; margin-bottom: 1px !important; margin-top: 2px !important; }
.opportunity { margin-bottom: 2px !important; padding-left: 8px !important; }
.opp-title { margin-bottom: 1px !important; font-size: 7.8pt !important; }
.opportunity p { font-size: 6.4pt !important; line-height: 1.25 !important; margin-bottom: 1px !important; }
p { font-size: 6.4pt !important; line-height: 1.25 !important; margin-bottom: 1px !important; }
.quick-fix { padding: 2px 6px !important; font-size: 6.2pt !important; line-height: 1.25 !important; margin-top: 1px !important; }
.summary-table { margin-top: 2px !important; margin-bottom: 2px !important; font-size: 6.6pt !important; }
.summary-table th { padding: 3px 6px !important; font-size: 6.4pt !important; }
.summary-table td { padding: 3px 6px !important; font-size: 6.4pt !important; }
.totals-row { padding: 3px 8px !important; margin-bottom: 2px !important; font-size: 6.4pt !important; }
.timeline { margin-top: 2px !important; margin-bottom: 2px !important; gap: 4px !important; }
.timeline-step { padding: 2px 4px !important; font-size: 5.7pt !important; line-height: 1.2 !important; }
.timeline-step .step-label { font-size: 5.7pt !important; margin-bottom: 1px !important; }
.metrics-row { margin-bottom: 2px !important; gap: 6px !important; }
.metric-box { padding: 2px 6px !important; }
.metric-box .metric-label { font-size: 5.4pt !important; margin-bottom: 1px !important; letter-spacing: 0.6px !important; }
.metric-box .metric-value { font-size: 7.2pt !important; }
.footer { padding-top: 2px !important; }
.footer-disclaimer { font-size: 5.8pt !important; margin-bottom: 2px !important; line-height: 1.2 !important; }
.footer-sig-left { font-size: 6.4pt !important; line-height: 1.3 !important; }
.footer-sig-left .name { font-size: 7pt !important; }
"""


def patch_html(html_path: Path) -> bool:
    """Inject CSS override just before </style>. Idempotent."""
    text = html_path.read_text(encoding="utf-8")
    if "BOTTOM-OVERFLOW FIX OVERRIDES" in text:
        # Already patched. Strip the old block first so we can re-inject latest.
        before, _, rest = text.partition("/* === BOTTOM-OVERFLOW FIX OVERRIDES")
        _, _, after = rest.partition("=== */")
        # `after` starts after the closing marker — find the next `</style>`
        text = before + after.lstrip()
    if "</style>" not in text:
        print(f"  SKIP — no </style> tag in {html_path.name}")
        return False
    new_text = text.replace("</style>", CSS_OVERRIDE + "\n</style>", 1)
    html_path.write_text(new_text, encoding="utf-8")
    return True


def render_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Render PDF via Chrome headless. Overwrites pdf_path."""
    html_url = "file:///" + str(html_path.resolve()).replace("\\", "/")
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  CHROME ERROR: {result.stderr[:200]}")
        return False
    return pdf_path.exists() and pdf_path.stat().st_size > 1000


def main():
    if not REPORTS_DIR.exists():
        print(f"ERROR: {REPORTS_DIR} does not exist. Run from repo root.")
        sys.exit(1)

    results = []
    for stem in TARGETS:
        html = REPORTS_DIR / f"{stem}_diagnosis.html"
        pdf = REPORTS_DIR / f"{stem}_diagnosis.pdf"

        print(f"\n[{stem}]")
        if not html.exists():
            print(f"  SKIP — HTML not found")
            results.append((stem, "missing"))
            continue

        patched = patch_html(html)
        if not patched:
            results.append((stem, "patch_failed"))
            continue
        print(f"  CSS override injected")

        rendered = render_pdf(html, pdf)
        if not rendered:
            print(f"  PDF render FAILED")
            results.append((stem, "render_failed"))
            continue
        size_kb = pdf.stat().st_size / 1024
        print(f"  PDF rendered ({size_kb:.1f} KB)")
        results.append((stem, "ok"))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    ok = sum(1 for _, s in results if s == "ok")
    for stem, status in results:
        marker = "OK" if status == "ok" else "FAIL"
        print(f"  [{marker}] {stem}: {status}")
    print(f"\n{ok}/{len(TARGETS)} fixed")


if __name__ == "__main__":
    main()
