"""Dux Machina Intent Signal Engine — central config.

FROZEN INTERFACE: Phase 1 collectors import these constants verbatim.
All secrets live in ~/.dux_intent/.env (NEVER in the repo).
"""
import json
import os
from pathlib import Path

REPO = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS")
DATA_HOME = Path.home() / ".dux_intent"          # OUTSIDE OneDrive (SQLite corrupts on sync)
DB_PATH   = DATA_HOME / "intent.db"
CACHE_DIR = DATA_HOME / "cache"                  # big SBA/OSHA CSVs cached here
ENV_FILE  = DATA_HOME / ".env"                   # loaded via python-dotenv; keys: DOL_API_KEY, BRIGHTDATA_API_TOKEN, SOCRATA_APP_TOKEN, INTENT_SPREADSHEET_ID
OUTPUT_DIR = REPO / "SALES_TEAM" / "outputs" / "prospecting"
OUTREACH_DIR = REPO / "SALES_TEAM" / "outputs" / "outreach"
MCP_CRED_PATH = Path.home() / ".google_workspace_mcp" / "credentials" / "sabaazeez12@gmail.com.json"

REGISTRY_PATH = Path(__file__).resolve().parent / "signal_registry.json"

_ENV_LOADED = False


def load_env():
    """Load ~/.dux_intent/.env once via python-dotenv. Safe if file is missing."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    try:
        from dotenv import load_dotenv
        if ENV_FILE.exists():
            load_dotenv(ENV_FILE)
    except ImportError:
        pass
    _ENV_LOADED = True


def get_env(key, default=None):
    """Read an env var after ensuring the .env file is loaded. Empty string -> default."""
    load_env()
    val = os.environ.get(key, "")
    return val if val else default


def load_registry():
    """Parse signal_registry.json and return the dict."""
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs():
    """Create data home, cache, and output dirs if missing."""
    for d in (DATA_HOME, CACHE_DIR, OUTPUT_DIR, OUTREACH_DIR):
        d.mkdir(parents=True, exist_ok=True)
