"""Galveston County Clerk lien/judgment collector (avenue: pe_distress).

Source UI:  https://ava.fidlar.com/TXGalveston/AvaWeb/#/search  (Fidlar AVA)
Underlying JSON API (verified live 2026-07-06 via browser devtools):
    POST https://ava.fidlar.com/TXGalveston/ScrapRelay.WebService.Ava/breeze/Search
    (Breeze.js/OData-style JSON; returns Party1/Party2/DocType/RecordedDate/
    DocumentNo). Free public search; supports business name, date range, and
    Document Types autocomplete (ST TAX LIEN, M & M LIEN, LIEN AFFD, ...).
    Verified sample: ST TAX LIEN 01/01/2026-present returned 156 rows,
    Party1=STATE OF TEXAS (claimant), Party2=debtor businesses (HEY MIKEY'S
    LLC, MAAC LOGISTICS LLC, ROYALTY MEAT, TESLA INC) — ideal pe_distress
    shape; Party2 is the debtor.

DISABLED (enabled:false in signal_registry.json) — WHY, verified 2026-07-06:
    The Breeze endpoint returns HTTP 401 without an Authorization: Bearer
    <JWT>. That JWT is minted client-side through an invisible reCAPTCHA-v3
    (score-based) flow and stored in localStorage `authorizationData`
    (access_token). v3 passes silently in a real browser, so a Chrome-MCP
    driven session can capture the token and this collector can replay the
    Breeze POST — but plain requests cannot mint the JWT, and solving/
    bypassing captchas is out of scope. Search itself is free (image viewing
    may be paid). Re-enable once a browser-driven token-mint step is wired.

Interim hook: if a captured token is placed in ~/.dux_intent/.env as
    GALVESTON_AVA_JWT=<access_token>
collect() will attempt the Breeze search with it (payload is a best-effort
Breeze query DOCUMENTED AS UNVERIFIED — expect to adjust it against real
devtools traffic when the token path is wired; failures surface as ERROR,
never as fabricated data). Without the token collect() returns SKIPPED.

Doc types (from the live autocomplete; exact server-side names to confirm
when wired): ST TAX LIEN and FED TAX LIEN map to state/federal tax lien
(mag 1.0), ABSTRACT OF JUDGMENT / JUDGMENT to judgment_filed (1.0),
M & M LIEN to mechanics (0.7), LIS PENDENS 0.6. The index exposes no
address: zip empty, entity_key "biz:{name_norm}|".

Self-test (from SALES_TEAM/tools/intent_engine/):
    python -m collectors.liens_galveston --self-test
Runs collect() for the last 30 days into a throwaway in-memory store
(SKIPPED without GALVESTON_AVA_JWT), writes NOTHING to the sheet, saves
fixtures/liens_galveston_sample.json documenting the gate.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import requests

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

import config  # noqa: E402
from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._liens_common import classify_lien, looks_business  # noqa: E402
from common.http import TIMEOUT, USER_AGENT  # noqa: E402
from common.normalize import entity_key as biz_entity_key  # noqa: E402

SOURCE_ID = "liens_galveston"
AVENUE = "pe_distress"

BREEZE_URL = ("https://ava.fidlar.com/TXGalveston/"
              "ScrapRelay.WebService.Ava/breeze/Search")
UI_URL = "https://ava.fidlar.com/TXGalveston/AvaWeb/#/search"

# doc type name -> (signal_type, lien_kind, magnitude); None = classify by
# claimant. Names came from the live autocomplete — confirm when wired.
DOC_TYPE_MAP = {
    "ABSTRACT OF JUDGMENT": ("judgment_filed", "abstract_of_judgment", 1.0),
    "JUDGMENT": ("judgment_filed", "judgment", 1.0),
    "FED TAX LIEN": ("lien_filed", "federal_tax_lien", 1.0),
    "ST TAX LIEN": ("lien_filed", "state_tax_lien", 1.0),
    "M & M LIEN": ("lien_filed", "mechanics_or_private_lien", 0.7),
    "LIEN AFFD": ("lien_filed", None, None),
    "LIS PENDENS": ("lien_filed", "lis_pendens", 0.6),
}

SKIP_MSG = (
    "GALVESTON_AVA_JWT not set in ~/.dux_intent/.env — the Fidlar AVA Breeze "
    "API 401s without a Bearer JWT minted via an invisible reCAPTCHA-v3 flow "
    "in a real browser (verified 2026-07-06). Capture "
    "localStorage.authorizationData.access_token from a Chrome session to "
    "enable; see module docstring."
)


class Collector(BaseCollector):
    avenue = AVENUE
    source_id = SOURCE_ID
    metros = ("houston",)

    def _breeze_search(self, jwt, doc_type, d_from, d_to):
        """Best-effort Breeze POST (UNVERIFIED payload — adjust against real
        devtools traffic when the browser token-mint step is wired)."""
        payload = {
            "SearchCriteria": {
                "DocumentTypes": [doc_type],
                "StartDate": d_from.strftime("%m/%d/%Y"),
                "EndDate": d_to.strftime("%m/%d/%Y"),
                "LastName": "",
                "FirstName": "",
            },
            "Skip": 0,
            "Take": 500,
        }
        resp = requests.post(
            BREEZE_URL, json=payload, timeout=TIMEOUT,
            headers={"Authorization": f"Bearer {jwt}",
                     "User-Agent": USER_AGENT})
        resp.raise_for_status()
        return resp.json()

    def _emit(self, store, row, doc_type, since):
        """Emit signals for one Breeze result row (Party2 = debtor)."""
        rdate = str(row.get("RecordedDate") or row.get("recordedDate") or "")[:10]
        try:
            fdate = date.fromisoformat(rdate)
        except (ValueError, TypeError):
            return 0, set()
        if fdate < since:
            return 0, set()
        signal_type, lien_kind, magnitude = DOC_TYPE_MAP[doc_type]
        claimants = [str(row.get("Party1") or row.get("party1") or "").strip()]
        claimants = [c for c in claimants if c]
        if magnitude is None:
            lien_kind, magnitude = classify_lien(claimants)
        debtor = str(row.get("Party2") or row.get("party2") or "").strip()
        if not debtor or not looks_business(debtor):
            return 0, set()
        docno = str(row.get("DocumentNo") or row.get("documentNo") or "")
        key = biz_entity_key(debtor, "")
        sig = Signal(
            entity_key=key,
            entity_name=debtor,
            metro="houston",
            avenue=self.avenue,
            signal_type=signal_type,
            signal_date=fdate.isoformat(),
            magnitude=magnitude,
            source_id=self.source_id,
            source_ref=docno or f"{doc_type} {fdate.isoformat()}",
            raw=dict(row),
            attrs={
                "lien_kind": lien_kind,
                "claimant": claimants[0] if claimants else "",
                "county": "GALVESTON",
                "instrument_type": doc_type,
            },
        )
        added = 1 if store.add_signal(sig) else 0
        return added, {key}

    def collect(self, since, store, registry):
        try:
            jwt = config.get_env("GALVESTON_AVA_JWT")
            if not jwt:
                return CollectorResult(self.source_id, 0, 0, "SKIPPED",
                                       SKIP_MSG)
            today = date.today()
            total_added = 0
            entities = set()
            errors = []
            any_ok = False
            for doc_type in DOC_TYPE_MAP:
                try:
                    data = self._breeze_search(jwt, doc_type, since, today)
                except Exception as exc:
                    errors.append(f"{doc_type}: {type(exc).__name__}: {exc}")
                    continue
                any_ok = True
                rows = data if isinstance(data, list) else (
                    data.get("Results") or data.get("results") or [])
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    added, keys = self._emit(store, row, doc_type, since)
                    total_added += added
                    entities |= keys
            if not any_ok:
                return CollectorResult(self.source_id, 0, 0, "ERROR",
                                       "; ".join(errors) or "all queries failed")
            status = "OK" if total_added else "EMPTY"
            return CollectorResult(self.source_id, total_added, len(entities),
                                   status, "; ".join(errors))
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


COLLECTOR = Collector()


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

def _self_test(days=30):
    from common.store import Store
    print(f"[{SOURCE_ID}] --self-test  (last {days} days, throwaway "
          f"in-memory store)")
    since = date.today() - timedelta(days=days)
    registry = config.load_registry()
    store = Store(":memory:")
    result = Collector().collect(since, store, registry)
    sigs = store.get_signals(avenue=AVENUE)
    by_type = Counter(s["signal_type"] for s in sigs)
    sample = json.loads(sigs[0]["raw"]) if sigs else None
    store.close()

    fixtures_dir = ENGINE_ROOT / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    fixture = {
        "source_id": SOURCE_ID,
        "captured": date.today().isoformat(),
        "live_status": result.status,
        "window_days": days,
        "enabled": False,
        "gate": ("Fidlar AVA Breeze API requires a Bearer JWT minted via "
                 "invisible reCAPTCHA-v3 in a real browser; endpoint 401s "
                 "otherwise (verified 2026-07-06). Interim: set "
                 "GALVESTON_AVA_JWT in ~/.dux_intent/.env from a Chrome "
                 "session's localStorage authorizationData.access_token."),
        "note": ("raw record behind the first emitted signal" if sample else
                 "no live data; " + (result.error or result.status)),
        "sample_record": sample,
        "signal_counts": dict(by_type),
        "breeze_url": BREEZE_URL,
    }
    fixture_path = fixtures_dir / f"{SOURCE_ID}_sample.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, default=str),
                            encoding="utf-8")

    print(f"  status={result.status} signals={result.signals_added} "
          f"entities={result.entities_seen}")
    if result.error:
        print(f"  detail: {result.error}")
    print(f"  fixture saved: {fixture_path}")
    print(f"  RESULT: {result.status}")
    return 0 if result.status in ("OK", "EMPTY", "SKIPPED") else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true",
                        help="collect last N days into a throwaway store; "
                             "writes nothing but fixtures/<source_id>_sample.json")
    parser.add_argument("--days", type=int, default=30,
                        help="self-test lookback window (default 30)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(_self_test(args.days))
    parser.print_help()
