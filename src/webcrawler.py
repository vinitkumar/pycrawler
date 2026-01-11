"""Webcrawler module."""


import re
import urllib.parse
from collections import deque
from traceback import format_exc

from src.linkfetcher import BrowserType, Linkfetcher


class Webcrawler:
    """Webcrawler class that contains the crawling logic."""

    def __init__(
        self,
        root: str,
        depth: int,
        locked: bool = True,
        browser: BrowserType = "chromium",
    ) -> None:
        """Initialize the webcrawler.

        Args:
            root: The starting URL to crawl from.
            depth: Maximum depth to traverse.
            locked: Whether to stay on the same host.
            browser: Browser User-Agent to use (chromium, firefox, brave, safari, edge).
        """
        self.root: str = root
        self.depth: int = depth
        self.locked: bool = locked
        self.browser: BrowserType = browser
        self.links: int = 0
        self.followed: int = 0
        self.urls: list[str] = []
        self.host: str = urllib.parse.urlparse(root)[1]

    def crawl(self) -> None:
        """Crawl the web starting from root URL.

        This method crawls URLs breadth-first up to the specified depth,
        collecting all discovered links.
        """
        page = Linkfetcher(self.root, browser=self.browser)
        page.linkfetch()
        queue: deque[str] = deque()
        for url in page.urls:
            queue.append(url)
        followed: list[str] = [self.root]
        n = 0

        while True:
            try:
                url = queue.pop()
                n += 1
                if url not in followed:
                    try:
                        host = urllib.parse.urlparse(url)[1]
                        if self.locked and re.match(f".*{self.host}", host):
                            followed.append(url)
                            self.followed += 1
                            page = Linkfetcher(url, browser=self.browser)
                            page.linkfetch()
                            for link in page:
                                if link not in self.urls:
                                    self.links += 1
                                    queue.append(link)
                                    self.urls.append(link)
                            if n > self.depth > 0:
                                break
                    except Exception as e:
                        print("Exception")
                        print(f"ERROR: The URL {url} can't be crawled {e}")
                        print(format_exc())
            except IndexError:
                break
