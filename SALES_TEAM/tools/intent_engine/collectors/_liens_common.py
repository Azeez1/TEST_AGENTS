"""Shared debtor/claimant heuristics for the county lien/judgment collectors
(liens_fortbend, liens_montgomery, liens_galveston, liens_brazoria).

Mirrors the (module-private) heuristics proven in collectors/liens_harris.py:
county lien indexes carry no entity type, so a name-token heuristic separates
business debtors from individuals, and the claimant name classifies a generic
LIEN into federal/state/municipal/mechanics kinds with the same magnitudes the
Harris collector uses (federal_tax 1.0 / state_tax 1.0 / municipal 0.6 /
mechanics_or_private 0.7). Not a collector — no Collector class, never
registered in signal_registry.json.
"""
import re

BUSINESS_TOKENS = {
    "LLC", "L.L.C", "INC", "CORP", "CORPORATION", "CO", "COMPANY", "LP",
    "LLP", "LTD", "PLLC", "PC", "PA", "ENTERPRISES", "ENTERPRISE", "HOLDINGS",
    "GROUP", "SERVICES", "SERVICE", "PARTNERS", "ASSOCIATES", "TRUCKING",
    "LOGISTICS", "TRANSPORT", "CONSTRUCTION", "BUILDERS", "CONTRACTORS",
    "RESTAURANT", "REPAIR", "INVESTMENTS", "PROPERTIES", "SOLUTIONS",
    "INDUSTRIES", "MANAGEMENT", "VENTURES", "AUTOMOTIVE", "MECHANICAL",
    "PLUMBING", "ELECTRIC", "ROOFING", "CONCRETE", "FABRICATION", "SUPPLY",
    "DISTRIBUTORS", "FOODS", "HOSPITALITY", "REALTY", "STUDIO", "CLINIC",
}
GOV_MARKERS = (
    "STATE OF", "CITY OF", "COUNTY", "UNITED STATES", "INTERNAL REVENUE",
    "US TREASURY", "U S TREASURY", "SCHOOL", "ISD", "AUTHORITY", "COMMISSION",
    "DEPARTMENT", "ATTORNEY GENERAL", "MUNICIPAL", "UTILITY DISTRICT",
    "COMPTROLLER", "ADMINISTRATION",
)
FEDERAL_MARKERS = ("INTERNAL REVENUE", "UNITED STATES", "US TREASURY",
                   "U S TREASURY", "IRS", "US SMALL BUSINESS", "U S SMALL")
STATE_TX_MARKERS = ("STATE OF TEXAS", "TEXAS WORKFORCE", "COMPTROLLER",
                    "ATTORNEY GENERAL", "EMPLOYMENT COMMISSION")
MUNI_MARKERS = ("CITY OF", "COUNTY", "MUNICIPAL", "UTILITY DISTRICT", "ISD",
                "SCHOOL DISTRICT", "AUTHORITY")


def looks_gov(name):
    up = name.upper()
    return any(m in up for m in GOV_MARKERS)


def looks_business(name):
    """True when the party name reads as a business (and not a gov body)."""
    if looks_gov(name):
        return False
    words = set(re.sub(r"[^\w\s]", " ", name.upper()).split())
    return bool(words & BUSINESS_TOKENS)


def classify_lien(claimants):
    """Map a generic LIEN record to (lien_kind, magnitude) from claimant names.

    Same table as liens_harris: federal/state tax liens are the strongest
    distress markers (1.0), municipal 0.6, everything else = mechanics or
    private lien 0.7.
    """
    joined = " | ".join(c.upper() for c in claimants)
    if any(m in joined for m in FEDERAL_MARKERS):
        return "federal_tax_lien", 1.0
    if any(m in joined for m in STATE_TX_MARKERS):
        return "state_tax_lien", 1.0
    if any(m in joined for m in MUNI_MARKERS):
        return "municipal_lien", 0.6
    return "mechanics_or_private_lien", 0.7
