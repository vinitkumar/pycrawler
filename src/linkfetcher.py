"""Linkfetcher Class."""


import threading
import urllib.parse
import urllib.request
from html import escape
from typing import TYPE_CHECKING, Literal
from urllib.error import HTTPError, URLError
from urllib.request import OpenerDirector, Request, build_opener

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from collections.abc import Iterator
from rich.progress import track

from src import LOGGER, __version__
from src.threading_utils import ThreadSafeList, ThreadSafeSet

# Browser User-Agent strings (latest stable versions as of 2025)
USER_AGENTS: dict[str, str] = {
    "chromium": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "firefox": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) "
        "Gecko/20100101 Firefox/134.0"
    ),
    "brave": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36 Brave/131"
    ),
    "safari": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/18.2 Safari/605.1.15"
    ),
    "edge": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    ),
}

BrowserType = Literal["chromium", "firefox", "brave", "safari", "edge"]


class Linkfetcher:
    """Link Fetcher class to abstract the link fetching.

    This class is thread-safe and can be used safely in concurrent operations,
    including with free-threaded Python (Python 3.13+ with GIL disabled).
    """

    def __init__(
        self,
        url: str,
        browser: BrowserType = "chromium",
        *,
        thread_safe: bool = False,
    ) -> None:
        """Initialize the Linkfetcher.

        Args:
            url: The URL to fetch links from.
            browser: Browser User-Agent to use.
            thread_safe: If True, use thread-safe data structures internally.
        """
        self.url: str = url
        self._thread_safe = thread_safe
        self._lock = threading.Lock()

        # Use thread-safe collections when requested
        if thread_safe:
            self._urls_safe: ThreadSafeList[str] = ThreadSafeList()
            self._broken_urls_safe: ThreadSafeList[str] = ThreadSafeList()
        else:
            self._urls: list[str] = []
            self._broken_urls: list[str] = []

        self.__version__: str = __version__
        self.browser: BrowserType = browser
        self.agent: str = USER_AGENTS.get(browser, USER_AGENTS["chromium"])

    @property
    def urls(self) -> list[str]:
        """Get the list of discovered URLs."""
        if self._thread_safe:
            return self._urls_safe.to_list()
        return self._urls

    @urls.setter
    def urls(self, value: list[str]) -> None:
        """Set the URLs list."""
        if self._thread_safe:
            with self._lock:
                self._urls_safe = ThreadSafeList()
                self._urls_safe.extend(value)
        else:
            self._urls = value

    @property
    def broken_urls(self) -> list[str]:
        """Get the list of broken URLs."""
        if self._thread_safe:
            return self._broken_urls_safe.to_list()
        return self._broken_urls

    @broken_urls.setter
    def broken_urls(self, value: list[str]) -> None:
        """Set the broken URLs list."""
        if self._thread_safe:
            with self._lock:
                self._broken_urls_safe = ThreadSafeList()
                self._broken_urls_safe.extend(value)
        else:
            self._broken_urls = value

    def _add_headers(self, request: Request) -> None:
        """Add User Agent headers for the request."""
        request.add_header("User-Agent", self.agent)

    def __getitem__(self, x: int) -> str:
        """Get item by index."""
        if self._thread_safe:
            return self._urls_safe.to_list()[x]
        return self._urls[x]

    def __len__(self) -> int:
        """Return the number of URLs found."""
        if self._thread_safe:
            return len(self._urls_safe)
        return len(self._urls)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the URLs."""
        if self._thread_safe:
            yield from self._urls_safe
        else:
            yield from self._urls

    def open(self) -> tuple[Request, OpenerDirector]:
        """Open the URL with urllib.request.

        Returns:
            A tuple containing the Request and OpenerDirector objects.
        """
        url = self.url
        request = Request(url)
        handle = build_opener()
        return (request, handle)

    def _add_url(self, url: str) -> bool:
        """Add a URL to the collection if not already present.

        Args:
            url: The URL to add.

        Returns:
            True if the URL was added, False if it was already present.
        """
        if self._thread_safe:
            # Use lock for thread-safe check-then-add
            with self._lock:
                current = self._urls_safe.to_list()
                if url not in current:
                    self._urls_safe.append(url)
                    return True
                return False
        else:
            if url not in self._urls:
                self._urls.append(url)
                return True
            return False

    def _add_broken_url(self, url: str) -> None:
        """Add a broken URL to the collection."""
        if self._thread_safe:
            self._broken_urls_safe.append(url)
        else:
            self._broken_urls.append(url)

    def _get_crawled_urls(self, handle: OpenerDirector, request: Request) -> None:
        """Parse HTML content and extract URLs.

        Main method where the crawler HTML content is parsed with
        BeautifulSoup and URLs are extracted from anchor tags.

        This method is thread-safe when thread_safe=True is set during init.
        """
        try:
            content = handle.open(request).read().decode("utf-8", errors="replace")
            soup = BeautifulSoup(content, "html.parser")
            tags = soup("a")
            for tag in track(tags):
                href = tag.get("href")
                if isinstance(href, str):
                    url = urllib.parse.urljoin(self.url, escape(href))
                    self._add_url(url)

        except HTTPError as error:
            self._add_broken_url(error.url)
            if error.code == 404:
                LOGGER.warning("%s -> %s", error, error.url)
            else:
                LOGGER.warning("%s for %s", error, error.url)

        except URLError as error:
            LOGGER.fatal("%s for %s", error, self.url)
            raise URLError("URL entered is Incorrect") from error

    def linkfetch(self) -> None:
        """Fetch all links from the URL.

        Public method to call the internal methods for link fetching.
        """
        request, handle = self.open()
        self._add_headers(request)
        if handle:
            self._get_crawled_urls(handle, request)
