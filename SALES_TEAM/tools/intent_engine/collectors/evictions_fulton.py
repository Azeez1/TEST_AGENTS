"""evictions_fulton — Fulton County Magistrate dispossessory filings (Atlanta).

Avenue: property_mgmt | Metro: atlanta | Source target: re:SearchGA
(https://researchga.tylerhost.net/CourtRecordsSearch/), Tyler-hosted statewide
GA court records search that covers Fulton Magistrate dispossessory cases.

STATUS: DISABLED in signal_registry.json (collectors_enabled.evictions_fulton =
false). The JSON backend exists but every search route is login-walled.

Probe evidence (2026-07-05, direct HTTP, no browser):
  * GET  /CourtRecordsSearch/api/search           -> 404 JSON: "No action was
    found on the controller 'Search'" — an ASP.NET Web API 'Search' controller
    exists behind /CourtRecordsSearch/api/.
  * GET  /CourtRecordsSearch/api/auth/claims      -> 200 JSON but jwt=null,
    basicUserSecurity=null, features={} for anonymous callers. The Angular SPA
    gates every search feature on these claims.
  * POST /CourtRecordsSearch/search               -> 302 to
    https://researchga.tylerhost.net/auth/login?signin=... (Tyler Identity
    Server). Case search requires a registered, logged-in session.
  * All 60+ SPA JS chunks were downloaded and grepped: the only api/ routes
    shipped to anonymous users are api/auth/claims and
    api/auth/removeCountyCookie; the case-search action names are never
    exposed pre-login, so they cannot be replayed without a real session.
  * Bright Data Web Unlocker does not help: the blocker is mandatory account
    login (OIDC redirect + session cookie), not JS rendering or anti-bot.

To enable later: create a free re:SearchGA account, capture an authenticated
session cookie + the search XHR (DevTools > Network while running a Fulton
Magistrate dispossessory search), store the cookie in ~/.dux_intent/.env as
RESEARCHGA_COOKIE, port the captured request into `_authenticated_search()`,
then flip collectors_enabled.evictions_fulton to true.

Self-test:  python -m collectors.evictions_fulton --self-test
    Re-probes the anonymous endpoints, saves the live probe evidence to
    fixtures/evictions_fulton_sample.json, and reports SKIPPED (0 signals).
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult  # noqa: E402
from common import http  # noqa: E402

BASE_URL = "https://researchga.tylerhost.net/CourtRecordsSearch/"
CLAIMS_URL = BASE_URL + "api/auth/claims"
SKIP_REASON = (
    "re:SearchGA case search is login-walled: anonymous api/auth/claims returns "
    "null security claims and POST /CourtRecordsSearch/search redirects to "
    "Tyler Identity login. Set RESEARCHGA_COOKIE in ~/.dux_intent/.env and "
    "implement _authenticated_search() before enabling."
)
_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def _authenticated_search(since, store):
    """Placeholder for the authenticated Fulton dispossessory search.

    The search XHR (action name + request body) is only discoverable from an
    authenticated browser session; it was not exposed to anonymous callers as
    of 2026-07-05. Implement by replaying the captured request with the
    RESEARCHGA_COOKIE session, filtering to Fulton Magistrate dispossessory
    filings since `since`, then emitting eviction_spike Signals per plaintiff
    entity (mirror collectors/evictions_harris.py for the baseline/snapshot
    logic).
    """
    raise NotImplementedError(
        "Authenticated re:SearchGA search not implemented — capture the search "
        "XHR from a logged-in session first (see module docstring)."
    )


class Collector(BaseCollector):
    avenue = "property_mgmt"
    source_id = "evictions_fulton"
    metros = ("atlanta",)

    def collect(self, since, store, registry):
        try:
            cookie = config.get_env("RESEARCHGA_COOKIE")
            if not cookie:
                return CollectorResult(
                    source_id=self.source_id,
                    signals_added=0,
                    entities_seen=0,
                    status="SKIPPED",
                    error=SKIP_REASON,
                )
            return _authenticated_search(since, store)
        except Exception as exc:  # noqa: BLE001 — contract: never raise
            return CollectorResult(
                source_id=self.source_id,
                signals_added=0,
                entities_seen=0,
                status="ERROR",
                error=f"{type(exc).__name__}: {exc}",
            )


def _probe_evidence():
    """Live-probe the anonymous surface and return the evidence payload."""
    evidence = {
        "target": BASE_URL,
        "probed_on": date.today().isoformat(),
        "conclusion": SKIP_REASON,
        "probes": {},
    }
    try:
        resp = http.fetch(CLAIMS_URL)
        evidence["probes"]["api/auth/claims"] = {
            "status_code": resp.status_code,
            "body": resp.json(),
        }
    except Exception as exc:  # noqa: BLE001
        evidence["probes"]["api/auth/claims"] = {
            "error": f"{type(exc).__name__}: {exc}"
        }
    try:
        resp = http.fetch(BASE_URL + "api/search")
    except Exception as exc:  # noqa: BLE001
        # 404 JSON proves the Search controller exists but hides its actions.
        body = getattr(getattr(exc, "response", None), "text", "")
        evidence["probes"]["api/search"] = {
            "error": f"{type(exc).__name__}: {exc}",
            "body_snippet": body[:300],
        }
    else:
        evidence["probes"]["api/search"] = {
            "status_code": resp.status_code,
            "body_snippet": resp.text[:300],
        }
    return evidence


def _self_test():
    from common.store import Store

    print(f"[{Collector.source_id}] self-test: last 30 days, in-memory store")
    store = Store(db_path=":memory:")
    since = date.today() - timedelta(days=30)

    result = Collector().collect(since, store, {})

    evidence = _probe_evidence()
    _FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    fixture_path = _FIXTURES_DIR / f"{Collector.source_id}_sample.json"
    fixture_path.write_text(json.dumps(evidence, indent=2, default=str),
                            encoding="utf-8")

    print(f"  status        : {result.status}")
    print(f"  signals_added : {result.signals_added}")
    print(f"  entities_seen : {result.entities_seen}")
    if result.error:
        print(f"  reason        : {result.error}")
    print(f"  fixture       : {fixture_path}")
    store.close()
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print("Usage: python -m collectors.evictions_fulton --self-test")
