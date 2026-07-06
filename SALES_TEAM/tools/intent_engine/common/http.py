"""HTTP helpers for collectors — retries, per-domain courtesy throttle, Socrata,
ArcGIS FeatureServer paging, and Bright Data Web Unlocker.

FROZEN INTERFACE — collectors reuse these instead of re-implementing HTTP:
    soda(dataset, params, domain="data.transportation.gov")
    arcgis_query(feature_server_url, where, out_fields="*", result_offset=0)
    brightdata_unlock(url)
    fetch(url, params=None, headers=None)
"""
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

USER_AGENT = "DuxIntentEngine/1.0 (research; contact: sabaazeez12@gmail.com)"
MAX_RETRIES = 3
BACKOFF_BASE = 2.0          # seconds: 2, 4, 8
THROTTLE_SECONDS = 1.5      # courtesy sleep per domain between requests
TIMEOUT = 60

_last_hit = {}              # domain -> monotonic timestamp of last request


def _throttle(domain):
    last = _last_hit.get(domain)
    if last is not None:
        wait = THROTTLE_SECONDS - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
    _last_hit[domain] = time.monotonic()


def fetch(url, params=None, headers=None):
    """Plain GET with retries + per-domain courtesy sleep. Returns requests.Response.

    Raises requests.HTTPError / RequestException after MAX_RETRIES failures.
    """
    domain = urlparse(url).netloc
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    last_exc = None
    for attempt in range(MAX_RETRIES):
        _throttle(domain)
        try:
            resp = requests.get(url, params=params, headers=hdrs, timeout=TIMEOUT)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code} from {domain}", response=resp)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            status = getattr(getattr(exc, "response", None), "status_code", None)
            # 4xx other than 429 will not improve on retry
            if status is not None and 400 <= status < 500 and status != 429:
                raise
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_BASE * (2 ** attempt))
    raise last_exc


def soda(dataset, params, domain="data.transportation.gov"):
    """Query a Socrata dataset, returning parsed JSON (list of dicts).

    dataset: the 4x4 dataset id (e.g. "az4n-8mr2"). Honors SOCRATA_APP_TOKEN
    from ~/.dux_intent/.env when present (higher rate limits).
    """
    url = f"https://{domain}/resource/{dataset}.json"
    headers = {}
    token = config.get_env("SOCRATA_APP_TOKEN")
    if token:
        headers["X-App-Token"] = token
    resp = fetch(url, params=params, headers=headers)
    return resp.json()


def arcgis_query(feature_server_url, where, out_fields="*", result_offset=0):
    """Query one page of an ArcGIS FeatureServer layer. Returns the parsed JSON dict
    (caller pages by bumping result_offset until 'exceededTransferLimit' is absent/false
    or 'features' comes back empty).
    """
    url = feature_server_url.rstrip("/") + "/query"
    params = {
        "where": where,
        "outFields": out_fields,
        "resultOffset": result_offset,
        "f": "json",
        "outSR": 4326,
        "returnGeometry": "false",
    }
    resp = fetch(url, params=params)
    data = resp.json()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"ArcGIS error from {feature_server_url}: {data['error']}")
    return data


def brightdata_unlock(url):
    """Fetch a protected URL through Bright Data Web Unlocker REST API.

    Returns response body text. Raises RuntimeError if BRIGHTDATA_API_TOKEN missing.
    """
    token = config.get_env("BRIGHTDATA_API_TOKEN")
    if not token:
        raise RuntimeError(
            "BRIGHTDATA_API_TOKEN not set in ~/.dux_intent/.env — cannot use Web Unlocker"
        )
    api_url = "https://api.brightdata.com/request"
    zone = config.get_env("BRIGHTDATA_ZONE") or "mcp_unlocker"
    payload = {"zone": zone, "url": url, "format": "raw"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    last_exc = None
    for attempt in range(MAX_RETRIES):
        _throttle("api.brightdata.com")
        try:
            resp = requests.post(api_url, json=payload, headers=headers, timeout=120)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code} from brightdata", response=resp)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_BASE * (2 ** attempt))
    raise last_exc
