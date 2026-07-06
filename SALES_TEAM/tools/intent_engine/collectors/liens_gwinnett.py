"""Gwinnett County GA lien collector (avenue: pe_distress, metro: atlanta).

WHAT IS LIVE (free, no login): GA Dept of Revenue state tax liens for
Gwinnett via GSCCCA's State Tax Lien search — see collectors/_gsccca.py for
the full 3-step WebForms flow, verified live 2026-07-06. Emits lien_filed
(lien_kind=state_tax_lien, magnitude 1.0) for business-looking debtors.

WHAT IS NOT COVERED YET (recon 2026-07-06, all verified live):
  * Gwinnett runs NO free county lien/judgment index.
    gwinnettcourts.com/deeds-and-land-records/ routes all deeds/liens/FIFA
    recording AND searching to GSCCCA. Case search is the Odyssey portal
    portal-gagwinnett.tylertech.cloud (name/case lookups only, no date-range
    enumeration; the vanity odyssey.gwinnettcourts.com times out). It also
    links re:SearchGA (account required, filer-oriented — see
    collectors/evictions_fulton.py for why that wall can't be scripted
    anonymously). Odyssey = v2 manual enrichment only.
  * FIFAs (GA money judgments on the General Execution Docket), federal tax
    liens, mechanics liens and lis pendens live in the GSCCCA statewide lien
    index — PAID. v2 unlock: Regular account $14.95/mo per user (unlimited
    index searching, pricing verified eff. 2025-07-01; Single-Use $5/4h only
    wins for one-off pulls). With credentials: login at
    https://apps.gsccca.org/login.asp, then POST
    https://search.gsccca.org/Lien/liennames.asp?Type=0 with txtSearchType=0,
    txtSearchName, txtPartyType=1 (debtor), txtInstrCode (2=FIFA, 3=Federal
    Tax Lien, 8=Lien, 9=Lis Pendens, 53=Mechanics, 12=Personal Property),
    intCountyID=67 (GWINNETT), txtFromDate/txtToDate, MaxRows, TableType.
    The wall is credentials, not anti-bot (anonymous POST bounces to
    login.asp; the site is directly fetchable — Bright Data does not help).
    Index lag observed ~2-4 weeks (dtSysGoodThru ran ~1 month behind).

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.liens_gwinnett --self-test
Collects the last 30 days into a throwaway in-memory store, prints status and
per-type counts, writes NOTHING to the sheet, and saves one raw sample record
to fixtures/liens_gwinnett_sample.json.
"""
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._gsccca import (  # noqa: E402
    COUNTY_IDS, GSCCCAStateTaxCollector, self_test_main)


class Collector(GSCCCAStateTaxCollector):
    source_id = "liens_gwinnett"
    county_name = "GWINNETT"
    county_id = COUNTY_IDS["GWINNETT"]


COLLECTOR = Collector()


if __name__ == "__main__":
    self_test_main(Collector, __doc__)
