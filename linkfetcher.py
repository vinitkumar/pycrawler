#!/usr/bin/python
"""Linkfetcher Class."""
from __future__ import absolute_import
from __future__ import print_function

import sys
import urllib.parse
import urllib.request
from html import escape

import six
from bs4 import BeautifulSoup


class Linkfetcher(object):
    """Link Fetcher class to abstract the link fetching."""

    def __init__(self, url):
        """ init function to intiate url and urls array."""
        self.url = url
        self.urls = []
        self.__version__ = "0.0.1"
        self.agent = "%s/%s" % (__name__, self.__version__)

    def _addHeaders(self, request):
        """ Add headers for the crawler"""
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
        return request, handle

    def fetch_links(self):
        """fetch links."""
        request, handle = self.open()
        self._addHeaders(request)
        if handle:
            try:
                content = six.text_type(handle.open(request).read(), "utf-8",
                                        errors="replace")
                soup = BeautifulSoup(content, "html.parser")
                tags = soup('a')
            except urllib.request.HTTPError as error:

                if error.code == 404:
                    print("ERROR: %s -> %s" % (error, error.url), file=sys.stderr)
                else:
                    print("ERROR: %s" % error, file=sys.stderr)
                tags = []

            except urllib.request.URLError as error:
                print("ERROR: %s" % error, file=sys.stderr)
                tags = []
            for tag in tags:
                href = tag.get("href")
                if href is not None:
                    url = urllib.parse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.urls.append(url)
