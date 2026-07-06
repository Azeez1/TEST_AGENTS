"""Refined bleed ranking: rates not counts, bus carriers excluded, min sample."""
import json, csv, math, urllib.request, urllib.parse

TEMP = r"C:/Users/sabaa/AppData/Local/Temp"
SCRATCH = r"C:/Users/sabaa/AppData/Local/Temp/claude/C--Users-sabaa-ONEDRIVE-DESKTOP-TEST-AGENTS/573b1bee-a685-4413-ba2a-9e473c5344e1/scratchpad"
OUT = r"C:/Users/sabaa/ONEDRIVE/DESKTOP/TEST_AGENTS/SALES_TEAM/outputs/prospecting"

scored = json.load(open(f"{SCRATCH}/houston_fleet_bleed.json"))
dots = [r["dot"] for r in scored]

# fetch bus_units for exclusion of passenger carriers
def soda(dataset, params):
    url = f"https://data.transportation.gov/resource/{dataset}.json?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

bus = {}
for i in range(0, len(dots), 60):
    batch = dots[i:i+60]
    inlist = ",".join(f"'{d}'" for d in batch)
    for row in soda("az4n-8mr2", {"$select": "dot_number,bus_units",
                                   "$where": f"dot_number in ({inlist})", "$limit": "100"}):
        bus[row["dot_number"]] = int(row.get("bus_units") or 0)

NATL_V, NATL_D = 0.207, 0.059
ranked = []
for r in scored:
    if bus.get(r["dot"], 0) > 0:            # passenger carriers out
        continue
    if r["inspections_24mo"] < 10:          # too little signal to rank
        continue
    v_ex = max(0.0, (r["veh_oos_rate"] or 0) - NATL_V)
    d_ex = max(0.0, (r["drv_oos_rate"] or 0) - NATL_D)
    unsafe_rate = r["unsafe_flags"] / r["inspections_24mo"]
    fatig_rate = r["fatigued_flags"] / r["inspections_24mo"]
    crash_pu = r["crashes_24mo"] / r["power_units"] if r["power_units"] else 0
    score = (v_ex * 100 * math.sqrt(min(r["veh_insp"], 200))
             + d_ex * 160 * math.sqrt(min(r["drv_insp"], 200))
             + crash_pu * 400
             + unsafe_rate * 60 + fatig_rate * 60)
    # rough annualized direct OOS cost: each OOS event ~ $1,000 (downtime, re-insp, load delay)
    ann_oos_events = (r["veh_oos"] + r["drv_oos"]) / 2  # 24mo window -> per year
    r2 = dict(r)
    r2["bleed_score"] = round(score, 1)
    r2["est_annual_oos_events"] = round(ann_oos_events, 1)
    ranked.append(r2)

ranked.sort(key=lambda x: -x["bleed_score"])
json.dump(ranked, open(f"{OUT}/houston_fleet_targets_2026-07-05.json", "w"), indent=1)
cols = ["bleed_score","dot","name","dba","power_units","drivers","mileage","mcs150_year",
        "inspections_24mo","veh_oos_rate","drv_oos_rate","crashes_24mo","injuries","tow_aways",
        "unsafe_flags","fatigued_flags","est_annual_oos_events","phone","email","street","zip"]
with open(f"{OUT}/houston_fleet_targets_2026-07-05.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in ranked: w.writerow(r)

print(f"{len(ranked)} ranked carriers saved")
print(f"{'#':>2} {'SCORE':>6} {'PU':>4} {'INSP':>5} {'vOOS%':>6} {'dOOS%':>6} {'CRSH':>4}  NAME / CONTACT")
for i, r in enumerate(ranked[:20], 1):
    vr = f"{(r['veh_oos_rate'] or 0)*100:.0f}%"
    dr = f"{(r['drv_oos_rate'] or 0)*100:.0f}%"
    email = r['email'][:34] if r['email'] else 'no email'
    print(f"{i:>2} {r['bleed_score']:>6} {r['power_units']:>4} {r['inspections_24mo']:>5} {vr:>6} {dr:>6} {r['crashes_24mo']:>4}  {r['name'][:42]} | {r['phone']} | {email}")
