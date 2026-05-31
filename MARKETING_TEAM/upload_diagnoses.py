"""Upload 10 PE diagnosis PDFs to Google Drive and print web_view_links."""
import sys
import os

# Run from MARKETING_TEAM/ so credentials resolve (token_drive.pickle is here)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))
from upload_to_drive import upload_to_drive

FOLDER_ID = "1QkAUOP9v4u3DugZjVcYUnaiT7pitN3sv"
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "outputs", "reports")

pdfs = [
    ("align_pentagon_ems_diagnosis.pdf", "Pentagon EMS — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("shore_safe_transportation_diagnosis.pdf", "SAFE Transportation Services — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("frontenac_beckway_diagnosis.pdf", "Beckway — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("trivest_thermal_concepts_diagnosis.pdf", "Thermal Concepts — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("huron_rampart_diagnosis.pdf", "Rampart Exterior Services — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("arsenal_thermosafe_diagnosis.pdf", "ThermoSafe — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("sverica_raken_diagnosis.pdf", "Raken — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("riverside_certified_collision_diagnosis.pdf", "Certified Collision Group — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("comvest_riccobene_diagnosis.pdf", "Riccobene Associates — Technology Lever Diagnosis — Dux Machina.pdf"),
    ("monomoy_jiffy_lube_diagnosis.pdf", "Jiffy Lube International — Technology Lever Diagnosis — Dux Machina.pdf"),
]

results = []
for filename, display_name in pdfs:
    pdf_path = os.path.join(REPORTS_DIR, filename)
    print(f"Uploading {filename}...", flush=True)
    result = upload_to_drive(pdf_path, display_name, FOLDER_ID)
    link = result["web_view_link"]
    print(f"  -> {link}", flush=True)
    results.append((filename, link))

print("\n--- LINKS ---")
for fname, link in results:
    print(f"{fname}|{link}")
