"""Linkfetcher Class."""

from __future__ import annotations

import urllib.parse
import urllib.request
from html import escape
from typing import TYPE_CHECKING
from urllib.error import HTTPError, URLError
from urllib.request import OpenerDirector, Request, build_opener

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from collections.abc import Iterator
from rich.progress import track

from src import LOGGER, __version__


class Linkfetcher:
    """Link Fetcher class to abstract the link fetching."""

    def __init__(self, url: str) -> None:
        self.url: str = url
        self.urls: list[str] = []
        self.broken_urls: list[str] = []
        self.__version__: str = __version__
        self.agent: str = f"{__name__}/{self.__version__}"

    def _add_headers(self, request: Request) -> None:
        """Add User Agent headers for the request."""
        request.add_header("User-Agent", self.agent)

    def __getitem__(self, x: int) -> str:
        """Get item by index."""
        return self.urls[x]

    def __len__(self) -> int:
        """Return the number of URLs found."""
        return len(self.urls)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the URLs."""
        yield from self.urls

    def open(self) -> tuple[Request, OpenerDirector]:
        """Open the URL with urllib.request.

        Returns:
            A tuple containing the Request and OpenerDirector objects.
        """
        url = self.url
        request = Request(url)
        handle = build_opener()
        return (request, handle)

    def _get_crawled_urls(self, handle: OpenerDirector, request: Request) -> None:
        """Parse HTML content and extract URLs.

        Main method where the crawler HTML content is parsed with
        BeautifulSoup and URLs are extracted from anchor tags.
        """
        try:
            content = handle.open(request).read().decode("utf-8", errors="replace")
            soup = BeautifulSoup(content, "html.parser")
            tags = soup("a")
            for tag in track(tags):
                href = tag.get("href")
                if isinstance(href, str):
                    url = urllib.parse.urljoin(self.url, escape(href))
                    if url not in self.urls:
                        self.urls.append(url)

        except HTTPError as error:
            self.broken_urls.append(error.url)
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
