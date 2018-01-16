#!/usr/bin/python
"""Linkfetcher Class."""
import sys
import asyncio
import urllib.request
import urllib.parse
import six
import logging
from bs4 import BeautifulSoup
from html import escape

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class Linkfetcher(object):
    """Link Fetcher class to abstract the link fetching."""

    def __init__(self, url):
        self.url = url
        self.urls = []
        self.__version__ = "2.0.0"
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
            content = six.text_type(handle.open(request).read(), "utf-8",
                                    errors="replace")
            soup = BeautifulSoup(content, "html.parser")
            tags = soup('a')
            for tag in tags:
                href = tag.get("href")
                if href is not None:
                    url = urllib.parse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.urls.append(url)

        except urllib.request.HTTPError as error:
            if error.code == 404:
                logger.warning("ERROR: %s -> %s for %s" % (error, error.url, self.url))
            else:
                logger.warning("ERROR: %s for %s" % (error, self.url))

        except urllib.request.URLError as error:
            logger.warning("ERROR: %s for %s" % (error, self.url))
            raise urllib.request.URLError("URL entered is Incorrect")


    def linkfetch(self):
        """"
        Public method to call the internal methods
        """
        request, handle = self.open()
        self._add_headers(request)
        if handle:
            self._get_crawled_urls(handle, request)


