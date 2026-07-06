"""Collector contract for the Intent Signal Engine.

FROZEN INTERFACE — Phase 1 collector modules implement BaseCollector exactly.
Every collector module MUST also support:
    python -m collectors.<name> --self-test
which collects the last 30 days into a throwaway store, prints status + counts,
writes NOTHING to the sheet, and saves one raw sample payload to
fixtures/<source_id>_sample.json
"""
import importlib
from dataclasses import dataclass, field


@dataclass
class Signal:
    entity_key: str          # e.g. "dot:2422093" or "biz:acme trucking|77041"
    entity_name: str
    metro: str               # "houston" | "atlanta"
    avenue: str              # "trucking"|"property_mgmt"|"mechanical"|"manufacturing"|"dead_listings"|"pe_distress"
    signal_type: str         # must match a key under avenue.signals in signal_registry.json
    signal_date: str         # ISO "YYYY-MM-DD"
    magnitude: float         # 0.0-1.0 normalized WITHIN this signal_type
    source_id: str           # collector id, e.g. "osha_dol"
    source_ref: str          # evidence URL or record id (shown to user as proof)
    raw: dict                # original record
    attrs: dict = field(default_factory=dict)   # optional phone/email/street/zip


@dataclass
class CollectorResult:
    source_id: str
    signals_added: int
    entities_seen: int
    status: str              # "OK" | "EMPTY" | "ERROR" | "SKIPPED"
    error: str = ""


class BaseCollector:
    avenue: str
    source_id: str
    metros: tuple            # e.g. ("houston","atlanta")

    def collect(self, since, store, registry) -> CollectorResult:
        # since = datetime.date; store = Store instance; registry = parsed signal_registry.json dict
        # MUST: emit Signals via store.add_signal(sig); snapshots via store.add_snapshot(...)
        # MUST NOT: score, export, or touch Google Sheets
        # MUST: catch its own source errors and return CollectorResult(status="ERROR", error=...) — never raise
        ...


def load_collectors(registry):
    """Import enabled collector modules by source_id and return their instances.

    Reads registry["collectors_enabled"]. For each enabled source_id, tries to
    import collectors.<source_id> and instantiate its `Collector` class (or a
    module-level COLLECTOR instance). Missing modules are tolerated (Phase 1
    adds them incrementally) and reported in the returned `missing` list.

    Returns (collectors: list[BaseCollector], missing: list[str], disabled: list[str])
    """
    enabled_map = registry.get("collectors_enabled", {})
    collectors, missing, disabled = [], [], []
    for source_id, enabled in enabled_map.items():
        if not enabled:
            disabled.append(source_id)
            continue
        try:
            mod = importlib.import_module(f"collectors.{source_id}")
        except ImportError:
            missing.append(source_id)
            continue
        inst = None
        if hasattr(mod, "Collector"):
            inst = mod.Collector()
        elif hasattr(mod, "COLLECTOR"):
            inst = mod.COLLECTOR
        if inst is None:
            missing.append(source_id)
            continue
        collectors.append(inst)
    return collectors, missing, disabled
