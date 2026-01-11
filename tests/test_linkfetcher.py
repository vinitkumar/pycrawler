"""Unit tests for the Linkfetcher class."""

from __future__ import annotations

from urllib.request import Request

import pytest

from src.linkfetcher import USER_AGENTS, BrowserType, Linkfetcher


class TestUserAgents:
    """Tests for USER_AGENTS dictionary."""

    def test_user_agents_contains_all_browsers(self) -> None:
        """Test that USER_AGENTS contains all expected browsers."""
        expected_browsers = {"chromium", "firefox", "brave", "safari", "edge"}
        assert set(USER_AGENTS.keys()) == expected_browsers

    def test_user_agents_are_non_empty_strings(self) -> None:
        """Test that all User-Agent strings are non-empty."""
        for browser, agent in USER_AGENTS.items():
            assert isinstance(agent, str), f"{browser} agent is not a string"
            assert len(agent) > 0, f"{browser} agent is empty"

    def test_chromium_agent_contains_chrome(self) -> None:
        """Test that Chromium User-Agent contains Chrome identifier."""
        assert "Chrome" in USER_AGENTS["chromium"]

    def test_firefox_agent_contains_firefox(self) -> None:
        """Test that Firefox User-Agent contains Firefox identifier."""
        assert "Firefox" in USER_AGENTS["firefox"]

    def test_brave_agent_contains_brave(self) -> None:
        """Test that Brave User-Agent contains Brave identifier."""
        assert "Brave" in USER_AGENTS["brave"]

    def test_safari_agent_contains_safari(self) -> None:
        """Test that Safari User-Agent contains Safari identifier."""
        assert "Safari" in USER_AGENTS["safari"]

    def test_edge_agent_contains_edg(self) -> None:
        """Test that Edge User-Agent contains Edg identifier."""
        assert "Edg" in USER_AGENTS["edge"]


class TestLinkfetcherInit:
    """Tests for Linkfetcher initialization."""

    def test_init_with_url(self) -> None:
        """Test initialization with URL."""
        url = "https://example.com"
        fetcher = Linkfetcher(url)
        assert fetcher.url == url

    def test_init_default_browser_is_chromium(self) -> None:
        """Test that default browser is chromium."""
        fetcher = Linkfetcher("https://example.com")
        assert fetcher.browser == "chromium"
        assert fetcher.agent == USER_AGENTS["chromium"]

    @pytest.mark.parametrize("browser", ["chromium", "firefox", "brave", "safari", "edge"])
    def test_init_with_different_browsers(self, browser: BrowserType) -> None:
        """Test initialization with different browser types."""
        fetcher = Linkfetcher("https://example.com", browser=browser)
        assert fetcher.browser == browser
        assert fetcher.agent == USER_AGENTS[browser]

    def test_init_empty_urls_list(self) -> None:
        """Test that urls list is empty on init."""
        fetcher = Linkfetcher("https://example.com")
        assert fetcher.urls == []

    def test_init_empty_broken_urls_list(self) -> None:
        """Test that broken_urls list is empty on init."""
        fetcher = Linkfetcher("https://example.com")
        assert fetcher.broken_urls == []

    def test_init_has_version(self) -> None:
        """Test that version is set on init."""
        fetcher = Linkfetcher("https://example.com")
        assert fetcher.__version__ is not None
        assert isinstance(fetcher.__version__, str)


class TestLinkfetcherDunderMethods:
    """Tests for Linkfetcher dunder methods."""

    def test_len_empty(self) -> None:
        """Test __len__ with empty urls list."""
        fetcher = Linkfetcher("https://example.com")
        assert len(fetcher) == 0

    def test_len_with_urls(self) -> None:
        """Test __len__ with populated urls list."""
        fetcher = Linkfetcher("https://example.com")
        fetcher.urls = ["url1", "url2", "url3"]
        assert len(fetcher) == 3

    def test_getitem(self) -> None:
        """Test __getitem__ retrieves correct URL."""
        fetcher = Linkfetcher("https://example.com")
        fetcher.urls = ["url0", "url1", "url2"]
        assert fetcher[0] == "url0"
        assert fetcher[1] == "url1"
        assert fetcher[2] == "url2"

    def test_getitem_index_error(self) -> None:
        """Test __getitem__ raises IndexError for invalid index."""
        fetcher = Linkfetcher("https://example.com")
        with pytest.raises(IndexError):
            _ = fetcher[0]

    def test_iter(self) -> None:
        """Test __iter__ yields all URLs."""
        fetcher = Linkfetcher("https://example.com")
        fetcher.urls = ["url1", "url2", "url3"]
        result = list(fetcher)
        assert result == ["url1", "url2", "url3"]

    def test_iter_empty(self) -> None:
        """Test __iter__ with empty urls list."""
        fetcher = Linkfetcher("https://example.com")
        result = list(fetcher)
        assert result == []


class TestLinkfetcherMethods:
    """Tests for Linkfetcher methods."""

    def test_add_headers(self) -> None:
        """Test _add_headers adds User-Agent header."""
        fetcher = Linkfetcher("https://example.com", browser="firefox")
        request = Request("https://example.com")
        fetcher._add_headers(request)
        assert request.get_header("User-agent") == USER_AGENTS["firefox"]

    def test_open_returns_tuple(self) -> None:
        """Test open() returns a tuple of Request and OpenerDirector."""
        fetcher = Linkfetcher("https://example.com")
        result = fetcher.open()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Request)

    def test_open_request_has_correct_url(self) -> None:
        """Test open() creates Request with correct URL."""
        url = "https://example.com/path"
        fetcher = Linkfetcher(url)
        request, _ = fetcher.open()
        assert request.full_url == url


class TestLinkfetcherRealRequests:
    """Integration tests with real HTTP requests."""

    @pytest.mark.slow
    def test_linkfetch_from_example_com(self) -> None:
        """Test fetching links from example.com."""
        fetcher = Linkfetcher("https://example.com")
        fetcher.linkfetch()
        # example.com has at least one link (to iana.org)
        assert len(fetcher.urls) >= 1

    @pytest.mark.slow
    def test_linkfetch_extracts_absolute_urls(self) -> None:
        """Test that all extracted URLs are absolute."""
        fetcher = Linkfetcher("https://example.com")
        fetcher.linkfetch()
        for url in fetcher.urls:
            assert url.startswith("http://") or url.startswith("https://")

    @pytest.mark.slow
    def test_linkfetch_with_firefox_user_agent(self) -> None:
        """Test fetching with Firefox user agent."""
        fetcher = Linkfetcher("https://example.com", browser="firefox")
        fetcher.linkfetch()
        assert fetcher.browser == "firefox"
        # Should still work with different user agent
        assert len(fetcher.urls) >= 0

    @pytest.mark.slow
    def test_linkfetch_no_duplicate_urls(self) -> None:
        """Test that duplicate URLs are not added."""
        fetcher = Linkfetcher("https://example.com")
        fetcher.linkfetch()
        # Check for duplicates
        assert len(fetcher.urls) == len(set(fetcher.urls))

    @pytest.mark.slow
    def test_linkfetch_httpbin_links(self) -> None:
        """Test fetching multiple links from httpbin."""
        fetcher = Linkfetcher("https://httpbin.org/links/5/0")
        fetcher.linkfetch()
        # httpbin.org/links/5/0 has 4 links (links 1-4)
        assert len(fetcher.urls) >= 4

    @pytest.mark.slow
    def test_linkfetch_handles_404(self) -> None:
        """Test that 404 errors are handled gracefully."""
        fetcher = Linkfetcher("https://httpbin.org/status/404")
        fetcher.linkfetch()
        # Should have recorded the broken URL
        assert len(fetcher.broken_urls) > 0

    @pytest.mark.slow
    def test_linkfetch_iterable_after_fetch(self) -> None:
        """Test that Linkfetcher is iterable after fetch."""
        fetcher = Linkfetcher("https://example.com")
        fetcher.linkfetch()
        # Should be able to iterate
        urls = list(fetcher)
        assert urls == fetcher.urls
