"""Cobb County GA lien collector (avenue: pe_distress, metro: atlanta).

WHAT IS LIVE (free, no login): GA Dept of Revenue state tax liens for Cobb
via GSCCCA's State Tax Lien search — see collectors/_gsccca.py for the full
3-step WebForms flow, verified live 2026-07-06. Emits lien_filed
(lien_kind=state_tax_lien, magnitude 1.0) for business-looking debtors.

WHAT IS NOT COVERED YET (recon 2026-07-06, all verified live):
  * Cobb is the ONE metro county with its own free index — LandmarkWeb at
    superiorcourtclerk.cobbcounty.gov/landmark — but it is BLOCKED for plain
    requests: the anonymous flow (GET /landmark -> GET
    /LandmarkWeb/Search/SetDisclaimer?disclaimerType=search -> GET
    /LandmarkWeb/search/index?theme=.blue&section=searchCriteriaDocuments ->
    POST /LandmarkWeb/Search/DocumentTypeSearch with doctype ids GED=78
    (FIFA/judgments), ABSJDG=2/ABSTJDG=3, FTL=75, LIEN=115, LISPEND=121,
    STATETX=203, up to 2000 rows) reaches the server and echoes the query but
    ALWAYS returns a zero-row scaffold (totalPages=0) to non-browser sessions
    — even 'SMITH' across all doc types 2024-2026 — and GetResultsForPage
    then 500s. The page carries a reCAPTCHA-v3 token gate
    (Search/StoreRecaptchaToken). DO NOT trust zero-row LandmarkWeb responses
    as data. All Cobb hosts also fail Python TLS verification (incomplete
    chain; ctsearch cert expired). v2 path: drive it with a real browser
    session (Chrome MCP / headless) or reverse-engineer the session +
    reCAPTCHA flow; that unlocks TRUE county-level FIFA/judgment coverage.
  * Fallback that works today for the full lien index: the PAID GSCCCA
    statewide lien index. v2 unlock: Regular account $14.95/mo per user
    (unlimited index searching, pricing verified eff. 2025-07-01). With
    credentials: login at https://apps.gsccca.org/login.asp, then POST
    https://search.gsccca.org/Lien/liennames.asp?Type=0 with txtSearchType=0,
    txtSearchName, txtPartyType=1 (debtor), txtInstrCode (2=FIFA, 3=Federal
    Tax Lien, 8=Lien, 9=Lis Pendens, 53=Mechanics, 12=Personal Property),
    intCountyID=33 (COBB), txtFromDate/txtToDate, MaxRows, TableType.
    The wall is credentials, not anti-bot. Index lag observed ~2-4 weeks.

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.liens_cobb --self-test
Collects the last 30 days into a throwaway in-memory store, prints status and
per-type counts, writes NOTHING to the sheet, and saves one raw sample record
to fixtures/liens_cobb_sample.json.
"""
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors._gsccca import (  # noqa: E402
    COUNTY_IDS, GSCCCAStateTaxCollector, self_test_main)


class Collector(GSCCCAStateTaxCollector):
    source_id = "liens_cobb"
    county_name = "COBB"
    county_id = COUNTY_IDS["COBB"]


COLLECTOR = Collector()


if __name__ == "__main__":
    self_test_main(Collector, __doc__)
