#!/usr/bin/env python3
"""
Auto Re-index (Non-Interactive)
Automatically re-indexes all documents without prompts
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

# Load environment variables
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

# Import and patch the indexer to skip input prompts
import importlib.util
spec = importlib.util.spec_from_file_location(
    "index_module",
    Path(__file__).parent / "index_compliance_frameworks.py"
)
module = importlib.util.module_from_spec(spec)

# Monkey-patch input() to auto-continue
original_input = __builtins__.input
__builtins__.input = lambda *args, **kwargs: print(f"Auto-continuing...") or ""

spec.loader.exec_module(module)

# Run the main function
if __name__ == "__main__":
    module.main()
