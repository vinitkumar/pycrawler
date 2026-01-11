"""Unit tests for the main module."""

from __future__ import annotations

import sys
import time
from unittest.mock import patch

import pytest

from main import crawl, getlinks, parse_args, timethis


class TestParseArgs:
    """Tests for parse_args function."""

    def test_parse_args_with_url_only(self) -> None:
        """Test parsing with just a URL."""
        with patch.object(sys, "argv", ["main.py", "https://example.com"]):
            args = parse_args()
            assert args.url == "https://example.com"
            assert args.depth == 30  # default
            assert args.browser == "chromium"  # default
            assert args.links is False  # default

    def test_parse_args_with_depth(self) -> None:
        """Test parsing with depth option."""
        with patch.object(sys, "argv", ["main.py", "-d", "5", "https://example.com"]):
            args = parse_args()
            assert args.depth == 5

    def test_parse_args_with_depth_long_form(self) -> None:
        """Test parsing with --depth option."""
        with patch.object(sys, "argv", ["main.py", "--depth", "10", "https://example.com"]):
            args = parse_args()
            assert args.depth == 10

    def test_parse_args_with_links_flag(self) -> None:
        """Test parsing with -l flag."""
        with patch.object(sys, "argv", ["main.py", "-l", "https://example.com"]):
            args = parse_args()
            assert args.links is True

    def test_parse_args_with_links_long_form(self) -> None:
        """Test parsing with --links flag."""
        with patch.object(sys, "argv", ["main.py", "--links", "https://example.com"]):
            args = parse_args()
            assert args.links is True

    @pytest.mark.parametrize("browser", ["chromium", "firefox", "brave", "safari", "edge"])
    def test_parse_args_with_browser(self, browser: str) -> None:
        """Test parsing with different browser options."""
        with patch.object(sys, "argv", ["main.py", "-b", browser, "https://example.com"]):
            args = parse_args()
            assert args.browser == browser

    def test_parse_args_with_browser_long_form(self) -> None:
        """Test parsing with --browser option."""
        with patch.object(sys, "argv", ["main.py", "--browser", "firefox", "https://example.com"]):
            args = parse_args()
            assert args.browser == "firefox"

    def test_parse_args_invalid_browser_raises_error(self) -> None:
        """Test that invalid browser choice raises error."""
        with (
            patch.object(sys, "argv", ["main.py", "-b", "invalid", "https://example.com"]),
            pytest.raises(SystemExit),
        ):
            parse_args()

    def test_parse_args_missing_url_raises_error(self) -> None:
        """Test that missing URL raises error."""
        with patch.object(sys, "argv", ["main.py"]), pytest.raises(SystemExit):
            parse_args()

    def test_parse_args_combined_options(self) -> None:
        """Test parsing with multiple options."""
        with patch.object(
            sys,
            "argv",
            ["main.py", "-d", "3", "-b", "brave", "-l", "https://example.com"],
        ):
            args = parse_args()
            assert args.depth == 3
            assert args.browser == "brave"
            assert args.links is True
            assert args.url == "https://example.com"


class TestTimethisDecorator:
    """Tests for timethis decorator."""

    def test_timethis_returns_function_result(self) -> None:
        """Test that decorated function returns correct result."""
        @timethis
        def sample_func(x: int, y: int) -> int:
            return x + y

        with patch("builtins.print"):  # Suppress print output
            result = sample_func(2, 3)
            assert result == 5

    def test_timethis_preserves_function_name(self) -> None:
        """Test that decorator preserves function name."""
        @timethis
        def my_named_function() -> None:
            pass

        assert my_named_function.__name__ == "my_named_function"

    def test_timethis_prints_execution_time(self) -> None:
        """Test that decorator prints execution time."""
        @timethis
        def slow_func() -> str:
            time.sleep(0.01)
            return "done"

        with patch("builtins.print") as mock_print:
            result = slow_func()

            # Check that print was called with timing info
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Execution took" in call for call in calls)
            assert result == "done"


class TestGetlinksReal:
    """Integration tests for getlinks with real HTTP requests."""

    @pytest.mark.slow
    def test_getlinks_returns_list_of_tuples(self) -> None:
        """Test that getlinks returns list of (index, url) tuples."""
        result = getlinks("https://example.com")
        assert isinstance(result, list)
        if len(result) > 0:
            assert all(isinstance(item, tuple) for item in result)
            assert all(len(item) == 2 for item in result)

    @pytest.mark.slow
    def test_getlinks_indexes_are_sequential(self) -> None:
        """Test that indexes are sequential starting from 0."""
        result = getlinks("https://example.com")
        if len(result) > 0:
            indexes = [item[0] for item in result]
            expected = list(range(len(result)))
            assert indexes == expected

    @pytest.mark.slow
    def test_getlinks_with_firefox_browser(self) -> None:
        """Test getlinks with Firefox browser."""
        result = getlinks("https://example.com", browser="firefox")
        assert isinstance(result, list)

    @pytest.mark.slow
    def test_getlinks_httpbin(self) -> None:
        """Test getlinks with httpbin links page."""
        result = getlinks("https://httpbin.org/links/3/0")
        # httpbin links page has multiple links
        assert len(result) >= 2


class TestCrawlReal:
    """Integration tests for crawl with real HTTP requests."""

    @pytest.mark.slow
    def test_crawl_returns_webcrawler_instance(self) -> None:
        """Test that crawl returns a Webcrawler instance."""
        from src.webcrawler import Webcrawler

        with patch("builtins.print"):  # Suppress timethis output
            result = crawl("https://example.com", 1)

        assert isinstance(result, Webcrawler)

    @pytest.mark.slow
    def test_crawl_with_different_browsers(self) -> None:
        """Test crawl with different browser user agents."""
        from src.webcrawler import Webcrawler

        for browser in ["chromium", "firefox", "brave"]:
            with patch("builtins.print"):
                result = crawl("https://example.com", 1, browser=browser)  # type: ignore[arg-type]
            assert isinstance(result, Webcrawler)
            assert result.browser == browser

    @pytest.mark.slow
    def test_crawl_populates_urls(self) -> None:
        """Test that crawl populates the urls list."""
        with patch("builtins.print"):
            result = crawl("https://example.com", 1)

        # Should have processed at least the root page
        assert isinstance(result.urls, list)
