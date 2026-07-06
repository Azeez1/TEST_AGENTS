"""Ability-to-pay collector: SBA FOIA loan join (source_id: pay_sba).

Joins EXISTING store entities (avenues pe_distress + manufacturing +
mechanical + trucking, both metros) to the SBA 7(a)/504 FOIA loan CSVs by
normalized borrower name and emits `credit_sba_loan` pay signals — a recent
SBA loan means a lender underwrote the business (Pain x Pay multiplier).
Spike (2026-07-06) proved pe_distress entities match SBA borrower names at
~40%+ with real multi-token matches (DOGS N SUDS, WEED PRO LAWN CARE, ...);
trucking matches its own pay source (FMCSA census) by construction and gets
this as extra credit data.

Data source: the CSVs already cached by collectors/sba_loans.py in
~/.dux_intent/cache/sba/*.csv (its _ensure_files machinery is reused, so a
cold cache downloads exactly like sba_loans does and a CKAN outage falls back
to stale cache). Files whose fiscal-year span ends before the pay window are
skipped without opening them.

Join rules (this collector's identity claim — the signal is emitted on the
matched entity's own entity_key, so it attaches at resolve conf 1.0):
    * normalized names equal (common/normalize.normalize_name, lower-cased)
    * name passes name_quality_ok (>= 2 tokens or >= 8 chars — kills
      single-short-word collisions)
    * the loan's metro (borrower state+zip, else project county/state) equals
      the entity's metro
    * zip-conflict veto: both zips present and different AND the name has
      < 3 tokens -> skipped (weakly distinctive name + conflicting location)

Signal contract (frozen v2):
    signal_type  credit_sba_loan   (registered under solvency_signals)
    magnitude    common.solvency.sba_credit_bucket(GrossApproval)
                 = .3/.5/.7/.9/1.0 at <50K/<250K/<1M/<5M/>=5M
    signal_date  ApprovalDate (the source-data date; solvency staleness-decays
                 with a 730d half-life and ignores > 1095d) — loans older than
                 PAY_MAX_AGE_DAYS are not emitted at all
    loan status  CANCLD/CHGOFF excluded (cancelled never funded; charged-off
                 is not evidence of ability to pay). PIF stays: repaid recent
                 debt IS credit evidence.

Self-test (seeds real-DB entities read-only into a throwaway store):
    python -m collectors.pay_sba --self-test [--cap N]
"""
import csv
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent.parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from collectors import BaseCollector, CollectorResult, Signal  # noqa: E402
from collectors._federal import metro_of, parse_date_any  # noqa: E402
from collectors._pay_common import (entity_name_index,  # noqa: E402
                                    pay_selftest_main)
from collectors.sba_loans import (DATASET_PAGE, NEEDED_COLS,  # noqa: E402
                                  SbaLoansCollector, _money)
from common.normalize import clean_zip, normalize_name  # noqa: E402
from common.solvency import PAY_MAX_AGE_DAYS, sba_credit_bucket  # noqa: E402

JOIN_AVENUES = ("pe_distress", "manufacturing", "mechanical", "trucking")
EXCLUDED_STATUSES = {"CANCLD", "CHGOFF"}   # PIF kept: repaid debt = credit
ZIP_VETO_MAX_TOKENS = 2                    # <3 tokens + zip conflict -> skip

_SPAN_RE = re.compile(r"fy(\d{4})-(\d{4}|present)")


def _file_may_have_recent(path, cutoff):
    """Skip CSVs whose fiscal-year span ends before the pay window.
    Unparseable filenames are scanned anyway (never skip on doubt)."""
    m = _SPAN_RE.search(path.name.lower())
    if not m:
        return True
    end = m.group(2)
    if end == "present":
        return True
    # FY end-year N covers approvals through Sep 30 of calendar year N
    return int(end) >= cutoff.year


class PaySbaCollector(BaseCollector):
    avenue = "pe_distress"          # natural avenue (spike-proven match rate)
    source_id = "pay_sba"
    metros = ("houston", "atlanta")

    def __init__(self):
        self.sample_payload = None

    # ------------------------------------------------------------- parsing

    def _iter_recent_metro_loans(self, path, registry, cutoff):
        """Yield (row_dict, approval_date, metro) for funded metro loans
        approved on/after cutoff. Streams the CSV row by row."""
        states = {str(m["state"]).upper()
                  for m in registry.get("metros", {}).values()}
        with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if not header:
                return
            idx = {str(h).strip().lower(): i for i, h in enumerate(header)}
            need = ("borrstate", "approvaldate", "borrname")
            if any(k not in idx for k in need):
                raise RuntimeError(f"{path.name}: missing columns "
                                   f"{[k for k in need if k not in idx]}")
            i_state = idx["borrstate"]
            i_pstate = idx.get("projectstate", i_state)
            for cells in reader:
                if len(cells) <= i_state:
                    continue
                st = cells[i_state].strip().upper()
                pst = (cells[i_pstate].strip().upper()
                       if len(cells) > i_pstate else "")
                if st not in states and pst not in states:
                    continue
                row = {k: (cells[i].strip() if len(cells) > i else "")
                       for k, i in idx.items() if k in NEEDED_COLS}
                status = str(row.get("loanstatus") or "").strip().upper()
                if status in EXCLUDED_STATUSES:
                    continue
                ad = parse_date_any(row.get("approvaldate"))
                if ad is None or ad < cutoff:
                    continue
                metro = metro_of(registry, row.get("borrstate"),
                                 zip5=row.get("borrzip"))
                if metro is None:
                    metro = metro_of(registry, row.get("projectstate"),
                                     county=row.get("projectcounty") or None)
                if metro is None:
                    continue
                yield row, ad, metro

    # --------------------------------------------------------------- join

    @staticmethod
    def _zip_conflict(entity, loan_zip, name_norm):
        """Veto weakly distinctive names when both sides claim different zips."""
        ez = (entity.get("zip") or "").strip()
        lz = clean_zip(loan_zip)
        if ez and lz and ez != lz:
            return len(name_norm.split()) <= ZIP_VETO_MAX_TOKENS
        return False

    def _emit(self, store, entity, row, approval):
        gross = _money(row.get("grossapproval"))
        loc_id = str(row.get("locationid") or "").strip()
        program = str(row.get("program") or "").strip() or "sba"
        ref_key = (f"{program}:{loc_id}" if loc_id else
                   f"{program}:{row.get('borrname')}|{row.get('approvaldate')}")
        sig = Signal(
            entity_key=entity["entity_key"],
            entity_name=entity["name"],
            metro=entity["metro"],
            avenue=entity["avenue"],           # entity identity untouched
            signal_type="credit_sba_loan",
            signal_date=approval.isoformat(),
            magnitude=sba_credit_bucket(gross),
            source_id=self.source_id,
            source_ref=f"{DATASET_PAGE}#{ref_key.replace(' ', '_')}",
            raw=dict(row),
            attrs={"gross_approval": gross,
                   "approval_date": approval.isoformat(),
                   "loan_program": program,
                   "loan_status": str(row.get("loanstatus") or ""),
                   "borrzip": clean_zip(row.get("borrzip")) or None},
        )
        return store.add_signal(sig)

    # ------------------------------------------------------------- collect

    def collect(self, since, store, registry):
        try:
            notes = []
            today = date.today()
            cutoff = today - timedelta(days=PAY_MAX_AGE_DAYS)
            index = entity_name_index(store, JOIN_AVENUES)
            if not index:
                return CollectorResult(
                    self.source_id, 0, 0, "EMPTY",
                    "no entities in store for avenues "
                    f"{'/'.join(JOIN_AVENUES)} — pay signals attach to "
                    "existing entities; run the pain collectors first")
            files = SbaLoansCollector()._ensure_files(notes)
            scanned = [f for f in files if _file_may_have_recent(f, cutoff)]
            skipped = [f.name for f in files if f not in scanned]
            if skipped:
                notes.append(f"skipped pre-window files: {', '.join(skipped)}")
            added, entities = 0, set()
            for path in scanned:
                for row, approval, metro in self._iter_recent_metro_loans(
                        path, registry, cutoff):
                    nn = normalize_name(row.get("borrname")).lower()
                    ents = index.get(nn)
                    if not ents:
                        continue
                    for ent in ents:
                        if ent.get("metro") != metro:
                            continue
                        if self._zip_conflict(ent, row.get("borrzip"), nn):
                            continue
                        if self._emit(store, ent, row, approval):
                            added += 1
                        entities.add(ent["entity_key"])
                        if self.sample_payload is None:
                            self.sample_payload = {
                                "matched_entity": {
                                    k: ent.get(k) for k in
                                    ("entity_key", "name", "avenue", "metro",
                                     "zip")},
                                "sba_loan": dict(row),
                                "source_file": path.name,
                            }
            status = "OK" if added > 0 else "EMPTY"
            return CollectorResult(self.source_id, added, len(entities),
                                   status, "; ".join(notes))
        except Exception as exc:
            return CollectorResult(self.source_id, 0, 0, "ERROR",
                                   f"{type(exc).__name__}: {exc}")


Collector = PaySbaCollector


if __name__ == "__main__":
    sys.exit(pay_selftest_main(Collector, JOIN_AVENUES, __doc__.splitlines()[0]))
