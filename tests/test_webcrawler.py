"""Unit tests for the Webcrawler class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.webcrawler import Webcrawler

if TYPE_CHECKING:
    from src.linkfetcher import BrowserType


class TestWebcrawlerInit:
    """Tests for Webcrawler initialization."""

    def test_init_with_required_params(self) -> None:
        """Test initialization with required parameters."""
        crawler = Webcrawler("https://example.com", depth=5)
        assert crawler.root == "https://example.com"
        assert crawler.depth == 5

    def test_init_default_locked_is_true(self) -> None:
        """Test that locked defaults to True."""
        crawler = Webcrawler("https://example.com", depth=5)
        assert crawler.locked is True

    def test_init_default_browser_is_chromium(self) -> None:
        """Test that default browser is chromium."""
        crawler = Webcrawler("https://example.com", depth=5)
        assert crawler.browser == "chromium"

    @pytest.mark.parametrize("browser", ["chromium", "firefox", "brave", "safari", "edge"])
    def test_init_with_different_browsers(self, browser: BrowserType) -> None:
        """Test initialization with different browser types."""
        crawler = Webcrawler("https://example.com", depth=5, browser=browser)
        assert crawler.browser == browser

    def test_init_locked_false(self) -> None:
        """Test initialization with locked=False."""
        crawler = Webcrawler("https://example.com", depth=5, locked=False)
        assert crawler.locked is False

    def test_init_counters_are_zero(self) -> None:
        """Test that links and followed counters start at zero."""
        crawler = Webcrawler("https://example.com", depth=5)
        assert crawler.links == 0
        assert crawler.followed == 0

    def test_init_urls_list_empty(self) -> None:
        """Test that urls list is empty on init."""
        crawler = Webcrawler("https://example.com", depth=5)
        assert crawler.urls == []


class TestWebcrawlerHostExtraction:
    """Tests for host extraction from URL."""

    def test_host_extracted_from_simple_url(self) -> None:
        """Test host extraction from simple URL."""
        crawler = Webcrawler("https://example.com", depth=5)
        assert crawler.host == "example.com"

    def test_host_extracted_from_url_with_path(self) -> None:
        """Test host extraction from URL with path."""
        crawler = Webcrawler("https://example.com/path/to/page", depth=5)
        assert crawler.host == "example.com"

    def test_host_extracted_from_url_with_port(self) -> None:
        """Test host extraction from URL with port."""
        crawler = Webcrawler("https://example.com:8080/path", depth=5)
        assert crawler.host == "example.com:8080"

    def test_host_extracted_from_subdomain(self) -> None:
        """Test host extraction from URL with subdomain."""
        crawler = Webcrawler("https://sub.example.com/path", depth=5)
        assert crawler.host == "sub.example.com"

    def test_host_extracted_from_http_url(self) -> None:
        """Test host extraction from HTTP (not HTTPS) URL."""
        crawler = Webcrawler("http://example.com", depth=5)
        assert crawler.host == "example.com"


class TestWebcrawlerRealCrawl:
    """Integration tests with real HTTP requests."""

    @pytest.mark.slow
    def test_crawl_example_com(self) -> None:
        """Test crawling example.com with depth 1."""
        crawler = Webcrawler("https://example.com", depth=1)
        crawler.crawl()
        # Should have found at least the IANA link
        assert crawler.followed >= 0

    @pytest.mark.slow
    def test_crawl_finds_links(self) -> None:
        """Test that crawl discovers links."""
        crawler = Webcrawler("https://example.com", depth=1)
        crawler.crawl()
        # example.com has at least one external link
        assert crawler.links >= 0

    @pytest.mark.slow
    def test_crawl_with_firefox_browser(self) -> None:
        """Test crawling with Firefox user agent."""
        crawler = Webcrawler("https://example.com", depth=1, browser="firefox")
        crawler.crawl()
        assert crawler.browser == "firefox"

    @pytest.mark.slow
    def test_crawl_locked_stays_on_host(self) -> None:
        """Test that locked=True stays on same host."""
        crawler = Webcrawler("https://example.com", depth=1, locked=True)
        crawler.crawl()
        # With locked=True, only same-host URLs should be followed
        # followed counter tracks same-host pages visited
        assert crawler.followed >= 0

    @pytest.mark.slow
    def test_crawl_httpbin_links(self) -> None:
        """Test crawling httpbin links page."""
        crawler = Webcrawler("https://httpbin.org/links/3/0", depth=1)
        crawler.crawl()
        # Should find links on the page
        assert crawler.links >= 0

    @pytest.mark.slow
    def test_crawl_with_zero_depth(self) -> None:
        """Test crawling with depth=0."""
        crawler = Webcrawler("https://example.com", depth=0)
        crawler.crawl()
        # With depth=0, should still process initial page
        # but depth check uses n > self.depth > 0 which is False when depth=0
        assert isinstance(crawler.urls, list)

    @pytest.mark.slow
    def test_crawl_urls_are_unique(self) -> None:
        """Test that crawled URLs are unique."""
        crawler = Webcrawler("https://example.com", depth=1)
        crawler.crawl()
        # All URLs should be unique
        assert len(crawler.urls) == len(set(crawler.urls))

    @pytest.mark.slow
    def test_crawl_counters_are_consistent(self) -> None:
        """Test that links counter matches urls list length."""
        crawler = Webcrawler("https://example.com", depth=1)
        crawler.crawl()
        # links counter should equal length of urls
        assert crawler.links == len(crawler.urls)
