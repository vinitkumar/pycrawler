#! /usr/bin/python
"""Linkfetcher Class."""
import urllib.request
import urllib.parse
from html import escape
import six
from bs4 import BeautifulSoup
from tqdm import tqdm
from src import LOGGER, __version__

class Linkfetcher:
    """Link Fetcher class to abstract the link fetching."""

    def __init__(self, url):
        self.url = url
        self.urls = []
        self.broken_urls = []
        self.__version__ = __version__
        self.agent = "%s/%s" % (__name__, self.__version__)

    def _add_headers(self, request):
        """Add User Agent headers for the request"""
        request.add_header("User-Agent", self.agent)

    def __getitem__(self, x):
        """Get item."""
        return self.urls[x]

    def open(self):
        """Open the URL with urllib.request."""
        url = self.url
        try:
            request = urllib.request.Request(url)
            handle = urllib.request.build_opener()
        except IOError:
            return None
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
            for tag in tqdm(tags, smoothing=True):
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
        """"
        Public method to call the internal methods
        """
        request, handle = self.open()
        self._add_headers(request)
        if handle:
            self._get_crawled_urls(handle, request)
