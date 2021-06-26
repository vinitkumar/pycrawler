#! /usr/bin/python
"""Linkfetcher Class."""
import urllib.parse
import urllib.request
from html import escape
from typing import List, Tuple, Any
from urllib.request import Request, build_opener, OpenerDirector

import six
from bs4 import BeautifulSoup
from rich.progress import track

from src import LOGGER, __version__


class Linkfetcher:
    """Link Fetcher class to abstract the link fetching."""

    def __init__(self, url: str) -> None:
        self.url: str = url
        self.urls: List[str] = []
        self.broken_urls: List[str] = []
        self.__version__: str = __version__
        self.agent: str = "%s/%s" % (__name__, self.__version__)

    def _add_headers(self, request: Request) -> None:
        """Add User Agent headers for the request"""
        request.add_header("User-Agent", self.agent)

    def __getitem__(self, x: int) -> str :
        """Get item."""
        return self.urls[x]

    def open(self) -> Tuple[Request, OpenerDirector]:
        """
            Open the URL with urllib.request.

            Don't know how to deal with build_opener type here
        """

        url = self.url
        request = Request(url)
        handle = build_opener()
        return (request, handle)

    def _get_crawled_urls(self, handle, request):
        """
        Main method where the crawler html content is parsed with
        beautiful soup and out of the DOM, we get the urls
        """
        try:
            content = six.text_type(
                handle.open(request).read(), "utf-8", errors="replace"
            )
            soup = BeautifulSoup(content, "html.parser")
            tags = soup("a")
            for tag in track(tags):
                href = tag.get("href")
                if href is not None:
                    url = urllib.parse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.urls.append(url)

        except urllib.request.HTTPError as error:
            self.broken_urls.append(error.url)
            if error.code == 404:
                LOGGER.warning(f"{error} -> {error.url}")
            else:
                LOGGER.warning(f"{error} for {error.url}")

        except urllib.request.URLError as error:
            LOGGER.fatal(f"{error} for {self.url}")
            raise urllib.request.URLError("URL entered is Incorrect")

    def linkfetch(self):
        """
        Public method to call the internal methods
        """
        request, handle = self.open()
        self._add_headers(request)
        if handle:
            self._get_crawled_urls(handle, request)
