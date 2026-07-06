"""Entity resolution — merge entities that are the same business across sources.

FROZEN INTERFACE — match ladder:
    exact entity_key match          -> 1.0
    name_norm + zip match           -> 0.9
    name_norm + metro match         -> 0.6  (flagged weak)
Cross-avenue signal stacking is allowed ONLY for members matched at >= 0.9.
Every output row carries match_conf.

API:
    resolve(store) -> (clusters, key_map)
        clusters: {canonical_entity_key: [ {entity_key, match_conf, weak}, ... ]}
        key_map:  {entity_key: {canonical, match_conf, weak}}
    signals_for_cluster(store, members, avenue, metro) -> list[(signal_dict, match_conf)]
"""
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

MATCH_EXACT = 1.0
MATCH_NAME_ZIP = 0.9
MATCH_NAME_METRO = 0.6
CROSS_AVENUE_MIN_CONF = 0.9


def resolve(store):
    """Cluster all entities in the store using the match ladder."""
    entities = {e["entity_key"]: e for e in store.iter_entities()}
    cluster_of = {k: k for k in entities}          # entity_key -> cluster id
    clusters = {k: {k: MATCH_EXACT} for k in entities}  # cluster id -> {member: conf}

    def merge(a, b, edge_conf):
        ca, cb = cluster_of[a], cluster_of[b]
        if ca == cb:
            return
        # absorb the smaller cluster into the larger one
        if len(clusters[cb]) > len(clusters[ca]):
            ca, cb = cb, ca
        for m, c in clusters[cb].items():
            clusters[ca][m] = min(c, edge_conf)
            cluster_of[m] = ca
        del clusters[cb]

    # Ladder rung 2: same normalized name + same 5-digit zip -> 0.9
    by_name_zip = {}
    for k, e in entities.items():
        nn = (e.get("name_norm") or "").strip().lower()
        z = (e.get("zip") or "").strip()
        if nn and z:
            by_name_zip.setdefault((nn, z), []).append(k)
    for keys in by_name_zip.values():
        for other in keys[1:]:
            merge(keys[0], other, MATCH_NAME_ZIP)

    # Ladder rung 3: same normalized name + same metro -> 0.6, flagged weak
    by_name_metro = {}
    for k, e in entities.items():
        nn = (e.get("name_norm") or "").strip().lower()
        metro = (e.get("metro") or "").strip().lower()
        if nn and metro:
            by_name_metro.setdefault((nn, metro), []).append(k)
    for keys in by_name_metro.values():
        for other in keys[1:]:
            merge(keys[0], other, MATCH_NAME_METRO)

    out_clusters = {}
    key_map = {}
    for members in clusters.values():
        # canonical = the member that was never absorbed (conf 1.0);
        # deterministic tie-break by first_seen then key
        canonical = sorted(
            members,
            key=lambda m: (-members[m],
                           entities[m].get("first_seen") or "9999-99-99", m),
        )[0]
        infos = []
        for m, c in members.items():
            conf = MATCH_EXACT if m == canonical else c
            info = {"entity_key": m, "match_conf": conf,
                    "weak": conf < CROSS_AVENUE_MIN_CONF}
            infos.append(info)
            key_map[m] = {"canonical": canonical, "match_conf": conf,
                          "weak": conf < CROSS_AVENUE_MIN_CONF}
        infos.sort(key=lambda i: (-i["match_conf"], i["entity_key"]))
        out_clusters[canonical] = infos
    return out_clusters, key_map


def signals_for_cluster(store, members, avenue, metro):
    """Gather (signal, match_conf) pairs for scoring one cluster in one avenue+metro.

    - Same-avenue signals: included from ALL members (weak 0.6 members allowed,
      but their conf flags the row as weak downstream).
    - Cross-avenue signals: included ONLY from members with match_conf >= 0.9
      (types unknown to the avenue are dropped later by score_entity anyway).
    """
    pairs = []
    for info in members:
        conf = info["match_conf"]
        for s in store.get_signals(entity_key=info["entity_key"], metro=metro):
            if s["avenue"] == avenue:
                pairs.append((s, conf))
            elif conf >= CROSS_AVENUE_MIN_CONF:
                pairs.append((s, conf))
    return pairs
