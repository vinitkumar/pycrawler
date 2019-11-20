""" Webcrawler module."""
import re
from traceback import format_exc
import urllib.parse
from collections import deque
from src import LOGGER
from src.linkfetcher import Linkfetcher


class Webcrawler:
    """Webcrawler class that contains the crawling logic."""

    def __init__(self, root, depth, locked=True):
        """ initialize variables."""
        self.root = root
        self.depth = depth
        self.locked = locked
        self.links = 0
        self.followed = 0
        self.urls = []
        self.host = urllib.parse.urlparse(root)[1]

    def crawl(self):
        """crawl function to return list of crawled urls."""
        page = Linkfetcher(self.root)
        page.linkfetch()
        queue = deque()
        for url in page.urls:
            queue.append(url)
        followed = [self.root]
        n = 0

        while True:
            try:
                url = queue.pop()
                n += 1
                if url not in followed:
                    try:
                        host = urllib.parse.urlparse(url)[1]
                        if self.locked and re.match(".*%s" % self.host, host):
                            followed.append(url)
                            self.followed += 1
                            page = Linkfetcher(url)
                            page.linkfetch()
                            # import ipdb; ipdb.set_trace()
                            for url in page:
                                if url not in self.urls:
                                    self.links += 1
                                    queue.append(url)
                                    self.urls.append(url)
                            if n > self.depth and self.depth > 0:
                                break
                    except Exception as e:
                        print("Exception")
                        print(f"ERROR: The URL {url} can't be crawled {e}")
                        print(format_exc())
            except IndexError:
                break


