"""Ability-to-pay collector: GA UCC-1 presence via GSCCCA (source_id: pay_ga_ucc).

STATUS: enabled:false in signal_registry.json — LOGIN-WALLED, verified live
2026-07-06. Never faked; collect() returns SKIPPED with the reason.

Intended signal (drop-in once unlocked): a recent UCC-1 financing statement
on file for an Atlanta-metro entity means a lender underwrote them = active
credit -> `credit_ucc_filing`, magnitude UCC_PRESENCE_CREDIT (0.6),
signal_date = the UCC filing date. GA-only by design: TX SOS UCC search is
paywalled too ($1/search SOSDirect), so there is no TX counterpart.

What was verified live (2026-07-06, plain requests with cookies + referer):
  * https://search.gsccca.org/UCC_Search/ (index page)         -> 200, free
  * search.asp?searchtype=Article9 (Basic Name Search FORM)    -> 200, free;
    form name=frmSearch POSTs to results.asp with fields:
        searchtype=Article9, ActionType='', SearchName='',
        debtorsearch=0 (organization), DebtorOrganizationName=<name>,
        exact=0|1, FromDate/ToDate (MM/DD/YYYY, index lags ~10 days),
        state=0 (statewide) | 1 + FinalCountyList, maxrows
  * POST results.asp (session cookies, referer set)             -> 200 BUT the
    body is a "Restrict Access" stub whose only content is a hidden form that
    auto-POSTs to https://apps.gsccca.org/login.asp?Redirect=/ucc_search/results.asp
    (setTimeout('document.frmLogin.submit()',100)). The RESULTS step requires
    a GSCCCA account login.

Why Bright Data does not help: BRIGHTDATA Web Unlocker defeats bot walls
(fingerprinting, CAPTCHAs, IP blocks). This is an AUTH wall — results are
served only to a logged-in session. Unlocking requires GSCCCA subscriber
credentials (paid: ~$24.95/mo single-user standard search subscription as of
verification), i.e. money + credentials, not proxy tech.

V2 unlock playbook (when EZ buys a subscription):
  1. POST apps.gsccca.org/login.asp with account credentials from env
     (GSCCCA_USER / GSCCCA_PASS via config.get_env — secrets stay in
     ~/.dux_intent/.env), keep the session cookie.
  2. Re-POST the verified frmSearch payload above per entity name
     (organization search, exact=0, FromDate = today - ~2y, statewide).
  3. Parse the results grid for UCC-1 rows (File Number, filed date, county);
     emit credit_ucc_filing per entity with the filing date; snapshot-gate on
     file numbers so re-runs stay idempotent. Cap names per run and reuse the
     courtesy-sleep pattern from collectors/_gsccca.py.

Self-test re-probes the wall live and reports honestly whether it still
stands (so a future flow change is noticed), then exits SKIPPED:
    python -m collectors.pay_ga_ucc --self-test
"""
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult  # noqa: E402
from common.http import TIMEOUT, USER_AGENT  # noqa: E402

SEARCH_PAGE = "https://search.gsccca.org/UCC_Search/search.asp?searchtype=Article9"
RESULTS_PAGE = "https://search.gsccca.org/UCC_Search/results.asp"
LOGIN_MARKER = "login.asp"

SKIP_NOTE = (
    "GSCCCA UCC Basic Name Search is LOGIN-WALLED at the results step: "
    "results.asp returns a 'Restrict Access' stub that auto-POSTs to "
    "apps.gsccca.org/login.asp (verified live 2026-07-06 with session "
    "cookies + referer). Auth wall, not bot wall — Bright Data Web Unlocker "
    "does not apply; needs a paid GSCCCA subscriber account. enabled:false "
    "in signal_registry.json; unlock playbook in the module docstring."
)


class PayGaUccCollector(BaseCollector):
    avenue = "pe_distress"
    source_id = "pay_ga_ucc"
    metros = ("atlanta",)

    def __init__(self):
        self.sample_payload = {"blocked": True, "reason": SKIP_NOTE}

    def collect(self, since, store, registry):
        # Paywalled source contract: enabled:false + documented, never faked.
        return CollectorResult(self.source_id, 0, 0, "SKIPPED", SKIP_NOTE)

    # ------------------------------------------------------------ probing

    def probe_wall(self):
        """Live re-check that the results step still bounces to login.
        Returns (still_walled: bool, detail: str). Used by --self-test only."""
        import requests
        try:
            s = requests.Session()
            s.headers.update({"User-Agent": USER_AGENT})
            r0 = s.get(SEARCH_PAGE, timeout=TIMEOUT)
            r0.raise_for_status()
            payload = {
                "searchtype": "Article9", "ActionType": "", "SearchName": "",
                "debtorsearch": "0", "DebtorLastName": "",
                "DebtorFirstName": "", "DebtorMiddleName": "",
                "DebtorOrganizationName": "WAFFLE HOUSE", "exact": "0",
                "FromDate": "01/01/2024", "ToDate": "06/01/2026",
                "state": "0", "maxrows": "100",
            }
            r1 = s.post(RESULTS_PAGE, data=payload, timeout=TIMEOUT,
                        headers={"Referer": SEARCH_PAGE})
            body = r1.text
            if LOGIN_MARKER in body and "Restrict Access" in body:
                return True, ("results.asp still bounces to login.asp "
                              f"(HTTP {r1.status_code}, {len(body)} bytes)")
            return False, ("results.asp did NOT bounce to login "
                           f"(HTTP {r1.status_code}, {len(body)} bytes) — "
                           "the wall may have lifted; revisit enabling this "
                           "collector via the docstring playbook")
        except Exception as exc:
            return True, (f"probe failed before reaching the wall: "
                          f"{type(exc).__name__}: {exc}")


Collector = PayGaUccCollector


def _self_test():
    from collectors._federal import write_fixture
    c = Collector()
    print(f"[self-test] {c.source_id}: paywalled source (enabled:false); "
          "re-probing the login wall live ...")
    walled, detail = c.probe_wall()
    print(f"[self-test] wall_still_up   = {walled}")
    print(f"[self-test] probe_detail    = {detail}")
    result = c.collect(None, None, None)
    print(f"[self-test] status          = {result.status}")
    print(f"[self-test] notes           = {result.error[:200]}...")
    c.sample_payload = {"blocked": True, "wall_still_up": walled,
                        "probe_detail": detail, "reason": SKIP_NOTE}
    path = write_fixture(c.source_id, c.sample_payload, result)
    print(f"[self-test] fixture -> {path}")
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="re-probe the GSCCCA login wall live, print "
                             "honest status, save fixture; no store writes")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test())
    parser.print_help()
    sys.exit(2)
