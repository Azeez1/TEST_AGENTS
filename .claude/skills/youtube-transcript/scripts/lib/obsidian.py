"""Obsidian vault file operations — write transcript notes to vault."""

import os
import re

# Default vault path
DEFAULT_VAULT_PATH = r"C:\Users\sabaa\OneDrive\Desktop\MEMORY\VAULT"
DEFAULT_SUBFOLDER = "YouTube Transcripts"


def get_vault_path() -> str:
    """Get the Obsidian vault path from config or default."""
    # Check for config override
    config_path = os.path.expanduser("~/.config/youtube-transcript/config.json")
    if os.path.exists(config_path):
        import json
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("vault_path", DEFAULT_VAULT_PATH)
    return DEFAULT_VAULT_PATH


def sanitize_filename(title: str) -> str:
    """Convert a video title to a safe filename."""
    # Remove or replace characters not allowed in filenames
    safe = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace multiple spaces/underscores with single space
    safe = re.sub(r'[\s_]+', ' ', safe).strip()
    # Truncate to reasonable length
    if len(safe) > 120:
        safe = safe[:120].rsplit(' ', 1)[0]
    return safe


def save_to_vault(
    content: str,
    title: str,
    subfolder: str = DEFAULT_SUBFOLDER,
    vault_path: str = None,
) -> str:
    """
    Save markdown content to the Obsidian vault.

    Returns the full path of the created file.
    """
    if vault_path is None:
        vault_path = get_vault_path()

    # Build target directory
    target_dir = os.path.join(vault_path, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    # Build filename
    filename = sanitize_filename(title) + ".md"
    filepath = os.path.join(target_dir, filename)

    # Handle duplicates
    if os.path.exists(filepath):
        base = sanitize_filename(title)
        counter = 1
        while os.path.exists(filepath):
            filename = f"{base} ({counter}).md"
            filepath = os.path.join(target_dir, filename)
            counter += 1

    # Write with UTF-8 encoding (critical for Windows)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
