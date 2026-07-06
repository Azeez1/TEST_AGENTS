"""Aggregate FMCSA SMS inspection + crash data for Houston carrier shortlist."""
import json, urllib.request, urllib.parse, time

TEMP = r"C:/Users/sabaa/AppData/Local/Temp"
OUT = r"C:/Users/sabaa/AppData/Local/Temp/claude/C--Users-sabaa-ONEDRIVE-DESKTOP-TEST-AGENTS/573b1bee-a685-4413-ba2a-9e473c5344e1/scratchpad"

carriers = json.load(open(f"{TEMP}/houston_carriers.json"))
dots = [c["dot_number"] for c in carriers]
print(f"{len(dots)} carriers")

def soda(dataset, params):
    url = f"https://data.transportation.gov/resource/{dataset}.json?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

# --- inspections: per-DOT aggregates over the SMS 24-month window ---
insp = {}
for batch in batched(dots, 40):
    inlist = ",".join(f"'{d}'" for d in batch)
    rows = soda("rbkj-cgst", {
        "$select": ("dot_number, count(*) as n_insp,"
                    "sum(vehicle_oos_total::number) as v_oos,"
                    "sum(driver_oos_total::number) as d_oos,"
                    "sum(oos_total::number) as t_oos,"
                    "sum(case(insp_level_id in ('1','2','5','6'), 1, true, 0)) as veh_insp,"
                    "sum(case(insp_level_id in ('1','2','3','6'), 1, true, 0)) as drv_insp,"
                    "sum(case(unsafe_insp='true', 1, true, 0)) as unsafe,"
                    "sum(case(fatigued_insp='true', 1, true, 0)) as fatigued"),
        "$where": f"dot_number in ({inlist})",
        "$group": "dot_number", "$limit": "100",
    })
    for r in rows:
        insp[r["dot_number"]] = r
    time.sleep(0.3)
print(f"inspection aggregates: {len(insp)}")

# --- crashes ---
crash = {}
for batch in batched(dots, 40):
    inlist = ",".join(f"'{d}'" for d in batch)
    rows = soda("4wxs-vbns", {
        "$select": ("dot_number, count(*) as n_crash,"
                    "sum(fatalities::number) as fatal,"
                    "sum(injuries::number) as inj,"
                    "sum(case(tow_away='true', 1, true, 0)) as tows"),
        "$where": f"dot_number in ({inlist})",
        "$group": "dot_number", "$limit": "100",
    })
    for r in rows:
        crash[r["dot_number"]] = r
    time.sleep(0.3)
print(f"crash aggregates: {len(crash)}")

# --- merge + score ---
NATL_V_OOS = 0.207   # national avg vehicle OOS rate
NATL_D_OOS = 0.059   # national avg driver OOS rate
out = []
for c in carriers:
    d = c["dot_number"]
    i = insp.get(d, {})
    k = crash.get(d, {})
    pu = int(c.get("power_units") or 0)
    n_insp = int(i.get("n_insp") or 0)
    veh_insp = int(i.get("veh_insp") or 0)
    drv_insp = int(i.get("drv_insp") or 0)
    v_oos = int(float(i.get("v_oos") or 0))
    d_oos = int(float(i.get("d_oos") or 0))
    n_crash = int(k.get("n_crash") or 0)
    v_rate = v_oos / veh_insp if veh_insp else None
    d_rate = d_oos / drv_insp if drv_insp else None
    # bleed score: how far above national average, weighted by exposure
    score = 0.0
    if v_rate is not None and veh_insp >= 5:
        score += max(0, v_rate - NATL_V_OOS) * 100 * min(veh_insp, 40) / 10
    if d_rate is not None and drv_insp >= 5:
        score += max(0, d_rate - NATL_D_OOS) * 150 * min(drv_insp, 40) / 10
    score += (n_crash / pu * 100) if pu else 0
    score += int(i.get("unsafe") or 0) * 0.5 + int(i.get("fatigued") or 0) * 0.5
    out.append({
        "dot": d, "name": c.get("legal_name"), "dba": c.get("dba_name") or "",
        "street": c.get("phy_street"), "zip": c.get("phy_zip"),
        "phone": c.get("phone"), "email": c.get("email_address") or "",
        "power_units": pu, "drivers": int(c.get("total_drivers") or 0),
        "mileage": int(c.get("mcs150_mileage") or 0),
        "mcs150_year": c.get("mcs150_mileage_year") or "",
        "op": c.get("carrier_operation"),
        "inspections_24mo": n_insp, "veh_insp": veh_insp, "drv_insp": drv_insp,
        "veh_oos": v_oos, "drv_oos": d_oos,
        "veh_oos_rate": round(v_rate, 3) if v_rate is not None else None,
        "drv_oos_rate": round(d_rate, 3) if d_rate is not None else None,
        "unsafe_flags": int(i.get("unsafe") or 0), "fatigued_flags": int(i.get("fatigued") or 0),
        "crashes_24mo": n_crash, "injuries": int(float(k.get("inj") or 0)),
        "fatalities": int(float(k.get("fatal") or 0)), "tow_aways": int(k.get("tows") or 0),
        "bleed_score": round(score, 1),
    })

out.sort(key=lambda x: -x["bleed_score"])
json.dump(out, open(f"{OUT}/houston_fleet_bleed.json", "w"), indent=1)
print(f"\nsaved {len(out)} scored carriers")
print(f"{'SCORE':>6} {'PU':>4} {'INSP':>5} {'vOOS%':>6} {'dOOS%':>6} {'CRSH':>4}  NAME")
for r in out[:25]:
    vr = f"{r['veh_oos_rate']*100:.0f}%" if r['veh_oos_rate'] is not None else "-"
    dr = f"{r['drv_oos_rate']*100:.0f}%" if r['drv_oos_rate'] is not None else "-"
    print(f"{r['bleed_score']:>6} {r['power_units']:>4} {r['inspections_24mo']:>5} {vr:>6} {dr:>6} {r['crashes_24mo']:>4}  {r['name'][:48]}")
