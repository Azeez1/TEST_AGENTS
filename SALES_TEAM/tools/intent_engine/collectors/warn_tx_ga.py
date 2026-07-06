"""WARN notice collector (avenue: manufacturing, source_id: warn_tx_ga).

Sources:
  TX — Socrata dataset 8w53-c4f6 on data.texas.gov (Texas WARN Act notices).
       Fields verified: notice_date, job_site_name, county_name, city_name,
       total_layoff_number, layoff_date, wfdd_received_date.
  GA — Georgia moved its WARN listing from dol.state.ga.us (legacy URL now 404,
       still attempted gracefully) to the Technical College System of Georgia:
       https://www.tcsg.edu/warn-public-view/  — a GravityView DataTables page.
       We POST its admin-ajax endpoint (action=gv_datatables_data, nonce scraped
       from the page) for the listing, then fetch each recent entry's detail
       page for county / zip / address / phone.

Emits `warn_notice` Signals. Magnitude scales with affected headcount
(sqrt(affected/500), capped at 1.0 — 50 affected ≈ 0.32, 500+ = 1.0).
Only employers in Houston / Atlanta metro counties are kept.
Entity identity = employer name + zip when known ("biz:{name_norm}|{zip}").
"""
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._federal import (  # noqa: E402
    clamp, metro_of, parse_date_any, selftest_main, strip_tags,
)
from common import http  # noqa: E402
from common.normalize import clean_zip, entity_key  # noqa: E402

TX_DATASET = "8w53-c4f6"
TX_DOMAIN = "data.texas.gov"
TX_ROW_LIMIT = 5000

GA_LEGACY_URL = ("https://www.dol.state.ga.us/public/es/warn/searchwarns/list"
                 "?geoArea=9&year={year}&step=search")
TCSG_LIST_URL = "https://www.tcsg.edu/warn-public-view/"
TCSG_AJAX_URL = "https://www.tcsg.edu/wp-admin/admin-ajax.php"
TCSG_PAGE_LEN = 100
TCSG_MAX_PAGES = 5
TCSG_MAX_DETAIL_FETCHES = 60

_GV_CONFIG_RE = re.compile(
    r'"view_id":(\d+),"post_id":(\d+),"nonce":"([0-9a-fA-F]+)"')


def _affected_magnitude(affected):
    if affected <= 0:
        return 0.1
    return clamp((affected / 500.0) ** 0.5, 0.1, 1.0)


def _to_int(value):
    try:
        return int(float(re.sub(r"[^\d.]", "", str(value)) or 0))
    except (TypeError, ValueError):
        return 0


class WarnTxGaCollector(BaseCollector):
    avenue = "manufacturing"
    source_id = "warn_tx_ga"
    metros = ("houston", "atlanta")

    def __init__(self):
        self.sample_payload = None

    # ------------------------------------------------------------------- TX

    def _collect_tx(self, since, store, registry):
        added, entities = 0, set()
        where = f"notice_date >= '{since.isoformat()}T00:00:00.000'"
        rows = http.soda(TX_DATASET, {"$where": where, "$limit": TX_ROW_LIMIT},
                         domain=TX_DOMAIN)
        for row in rows:
            name = str(row.get("job_site_name") or "").strip()
            if not name:
                continue
            nd = parse_date_any(row.get("notice_date"))
            if nd is None or nd < since:
                continue
            metro = metro_of(registry, "TX", county=row.get("county_name"),
                             city=row.get("city_name"))
            if metro is None:
                continue
            affected = _to_int(row.get("total_layoff_number"))
            ek = entity_key(name, "")
            source_ref = (f"https://data.texas.gov/resource/{TX_DATASET}.json"
                          f"?job_site_name={quote(name)}")
            sig = Signal(
                entity_key=ek,
                entity_name=name,
                metro=metro,
                avenue=self.avenue,
                signal_type="warn_notice",
                signal_date=nd.isoformat(),
                magnitude=_affected_magnitude(affected),
                source_id=self.source_id,
                source_ref=source_ref,
                raw=dict(row),
                attrs={"city": str(row.get("city_name") or "") or None},
            )
            if store.add_signal(sig):
                added += 1
            entities.add(ek)
            store.add_snapshot(self.source_id, date.today(),
                               f"tx:{nd.isoformat()}:{name}",
                               {"affected": affected,
                                "county": row.get("county_name")})
            if self.sample_payload is None:
                self.sample_payload = {"tx_warn_row": dict(row)}
            else:
                self.sample_payload.setdefault("tx_warn_row", dict(row))
        return added, entities

    # ------------------------------------------------------------ GA legacy

    def _collect_ga_legacy(self, since, store, registry):
        """Legacy GA DOL listing — currently 404 (moved to TCSG). Attempted for
        completeness; any failure is reported as a soft note, never fatal."""
        years = {since.year, date.today().year}
        rows_found = 0
        for year in sorted(years):
            resp = http.fetch(GA_LEGACY_URL.format(year=year))
            html_text = resp.text
            if "<table" not in html_text.lower():
                raise RuntimeError("no table in legacy GA DOL response")
            rows_found += len(re.findall(r"<tr", html_text, re.I)) - 1
        # The legacy page has been retired; if it ever returns real rows this
        # branch can be extended. For now just report what we saw.
        raise RuntimeError(f"legacy page responded but is unparsed "
                           f"({rows_found} <tr> rows) — TCSG is the primary")

    # -------------------------------------------------------------- GA TCSG

    def _post(self, url, data, referer):
        """Small throttled POST helper (common/http.py exposes GET only)."""
        import requests
        headers = {"User-Agent": http.USER_AGENT, "Referer": referer}
        last_exc = None
        for attempt in range(http.MAX_RETRIES):
            time.sleep(http.THROTTLE_SECONDS if attempt == 0
                       else http.BACKOFF_BASE * (2 ** (attempt - 1)))
            try:
                resp = requests.post(url, data=data, headers=headers,
                                     timeout=http.TIMEOUT)
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                last_exc = exc
        raise last_exc

    @staticmethod
    def _row_cells(row):
        if isinstance(row, dict):
            return [row.get(str(i), "") for i in range(5)]
        if isinstance(row, list):
            return list(row[:5]) + [""] * max(0, 5 - len(row))
        return [""] * 5

    def _tcsg_listing(self, since):
        """Yield dicts {warn_id, company, submitted(date), affected, entry_id, url}
        for entries submitted on/after `since` (listing ordered newest first)."""
        page_html = http.fetch(TCSG_LIST_URL).text
        m = _GV_CONFIG_RE.search(page_html)
        if not m:
            raise RuntimeError("could not find GravityView config/nonce on "
                               "tcsg.edu/warn-public-view")
        view_id, post_id, nonce = m.groups()
        for page in range(TCSG_MAX_PAGES):
            data = {
                "action": "gv_datatables_data",
                "view_id": view_id, "post_id": post_id, "nonce": nonce,
                "getData": "false", "hideUntilSearched": "0",
                "setUrlOnSearch": "true", "noEntriesOption": "0",
                "redirectURL": "",
                "draw": str(page + 1),
                "start": str(page * TCSG_PAGE_LEN),
                "length": str(TCSG_PAGE_LEN),
                "order[0][column]": "2", "order[0][dir]": "desc",
                "columns[2][name]": "gv_date_created",
            }
            resp = self._post(TCSG_AJAX_URL, data, TCSG_LIST_URL)
            payload = resp.json()
            rows = payload.get("data") or []
            if not rows:
                break
            stop = False
            for row in rows:
                cells = self._row_cells(row)
                submitted = parse_date_any(strip_tags(cells[2]))
                if submitted is None:
                    continue
                if submitted < since:
                    stop = True
                    break
                href = re.search(r'href="([^"]*?/entry/(\d+)/?[^"]*)"',
                                 str(cells[0]))
                entry_id = (href.group(2) if href
                            else strip_tags(cells[4]) or "")
                url = (href.group(1).replace("\\/", "/") if href else
                       f"{TCSG_LIST_URL}entry/{entry_id}/")
                yield {
                    "warn_id": strip_tags(cells[0]),
                    "company": strip_tags(cells[1]),
                    "submitted": submitted,
                    "affected": _to_int(strip_tags(cells[3])),
                    "entry_id": str(entry_id),
                    "url": url,
                    "_raw_row": row,
                }
            if stop or len(rows) < TCSG_PAGE_LEN:
                break

    @staticmethod
    def _parse_entry_fields(html_text):
        """Parse GravityView single-entry tables into [(label, value), ...]."""
        fields = []
        for tr in re.findall(r'<tr[^>]*id="gv-field-[^"]*"[^>]*>(.*?)</tr>',
                             html_text, re.S):
            lm = re.search(r'class="gv-field-label"[^>]*>(.*?)</', tr, re.S)
            tm = re.search(r"<td[^>]*>(.*?)</td>", tr, re.S)
            if lm and tm:
                fields.append((strip_tags(lm.group(1)), strip_tags(tm.group(1))))
        return fields

    def _collect_ga_tcsg(self, since, store, registry):
        added, entities = 0, set()
        detail_fetches = 0
        for item in self._tcsg_listing(since):
            if detail_fetches >= TCSG_MAX_DETAIL_FETCHES:
                break
            detail_fetches += 1
            county = zip_code = street = phone = ""
            fields = []
            try:
                detail_html = http.fetch(item["url"]).text
                fields = self._parse_entry_fields(detail_html)
                zips = []
                for label, value in fields:
                    ll = label.lower()
                    if ll == "county" and not county:
                        county = value
                    elif ll == "zip code":
                        zips.append(value)
                    elif ll == "company address" and not street:
                        street = re.sub(r"\s*Map It\s*$", "", value,
                                        flags=re.I).strip(" ,")
                    elif ll == "phone" and not phone:
                        phone = value
                    elif ll in ("total number of affected employees",
                                "number of employees affected"):
                        item["affected"] = max(item["affected"], _to_int(value))
                zip_code = clean_zip(zips[0]) if zips else ""
            except Exception:
                pass  # keep the listing row even if the detail page fails
            metro = metro_of(registry, "GA", county=county or None,
                             zip5=zip_code or None)
            if metro is None:
                continue
            name = item["company"]
            if not name:
                continue
            ek = entity_key(name, zip_code)
            sig = Signal(
                entity_key=ek,
                entity_name=name,
                metro=metro,
                avenue=self.avenue,
                signal_type="warn_notice",
                signal_date=item["submitted"].isoformat(),
                magnitude=_affected_magnitude(item["affected"]),
                source_id=self.source_id,
                source_ref=item["url"],
                raw={"listing": {k: v for k, v in item.items()
                                 if k != "_raw_row"},
                     "detail_fields": fields},
                attrs={"zip": zip_code or None, "street": street or None,
                       "phone": phone or None},
            )
            if store.add_signal(sig):
                added += 1
            entities.add(ek)
            store.add_snapshot(self.source_id, date.today(),
                               f"ga:{item['warn_id'] or item['entry_id']}",
                               {"affected": item["affected"], "county": county})
            if self.sample_payload is None or "ga_warn_entry" not in self.sample_payload:
                sample = {"listing": {k: v for k, v in item.items()
                                      if k != "_raw_row"},
                          "detail_fields": fields}
                if self.sample_payload is None:
                    self.sample_payload = {"ga_warn_entry": sample}
                else:
                    self.sample_payload["ga_warn_entry"] = sample
        return added, entities

    # -------------------------------------------------------------- collect

    def collect(self, since, store, registry):
        try:
            added, entities, notes = 0, set(), []
            sources_ok = 0

            try:
                a, e = self._collect_tx(since, store, registry)
                added += a
                entities |= e
                sources_ok += 1
            except Exception as exc:
                notes.append(f"tx: {type(exc).__name__}: {exc}")

            try:
                self._collect_ga_legacy(since, store, registry)
                sources_ok += 1
            except Exception as exc:
                notes.append(f"ga-legacy: {type(exc).__name__}: "
                             f"{str(exc)[:120]} (expected — moved to TCSG)")

            try:
                a, e = self._collect_ga_tcsg(since, store, registry)
                added += a
                entities |= e
                sources_ok += 1
            except Exception as exc:
                notes.append(f"ga-tcsg: {type(exc).__name__}: {exc}")

            note = "; ".join(notes)
            if sources_ok == 0:
                return CollectorResult(self.source_id, 0, 0, "ERROR",
                                       note or "all WARN sources failed")
            status = "OK" if added > 0 else "EMPTY"
            return CollectorResult(self.source_id, added, len(entities), status,
                                   note)
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


Collector = WarnTxGaCollector


if __name__ == "__main__":
    sys.exit(selftest_main(Collector))
