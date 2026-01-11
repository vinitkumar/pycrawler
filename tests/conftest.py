"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest

# Test URLs for real HTTP tests
TEST_URL = "https://example.com"
TEST_URL_WITH_LINKS = "https://httpbin.org/links/5/0"


@pytest.fixture
def test_url() -> str:
    """Provide a simple test URL."""
    return TEST_URL


@pytest.fixture
def test_url_with_links() -> str:
    """Provide a URL that has multiple links."""
    return TEST_URL_WITH_LINKS
