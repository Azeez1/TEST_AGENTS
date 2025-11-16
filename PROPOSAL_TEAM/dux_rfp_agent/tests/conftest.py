"""
Pytest configuration and fixtures.
"""

import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "integration: Integration tests requiring API keys")
    config.addinivalue_line("markers", "slow: Slow tests that may take time")
