"""Webcrawler module."""


import queue
import re
import threading
import urllib.parse
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import TYPE_CHECKING

from src.linkfetcher import BrowserType, Linkfetcher
from src.threading_utils import (
    ThreadSafeCounter,
    ThreadSafeList,
    ThreadSafeSet,
    get_optimal_worker_count,
    is_gil_disabled,
)

if TYPE_CHECKING:
    from concurrent.futures import Future


class Webcrawler:
    """Webcrawler class that contains the crawling logic.

    This class supports both sequential and concurrent crawling modes.
    Concurrent mode takes full advantage of free-threaded Python
    (Python 3.13+ with GIL disabled) for true parallel execution.
    """

    def __init__(
        self,
        root: str,
        depth: int,
        locked: bool = True,
        browser: BrowserType = "chromium",
        *,
        concurrent: bool = False,
        max_workers: int | None = None,
    ) -> None:
        """Initialize the webcrawler.

        Args:
            root: The starting URL to crawl from.
            depth: Maximum depth to traverse.
            locked: Whether to stay on the same host.
            browser: Browser User-Agent to use (chromium, firefox, brave, safari, edge).
            concurrent: If True, use concurrent crawling with thread pool.
            max_workers: Maximum number of worker threads for concurrent mode.
                        Defaults to automatic based on GIL status and task count.
        """
        self.root: str = root
        self.depth: int = depth
        self.locked: bool = locked
        self.browser: BrowserType = browser
        self.concurrent: bool = concurrent
        self.max_workers: int | None = max_workers
        self.host: str = urllib.parse.urlparse(root)[1]

        # Thread-safe counters and collections for concurrent mode
        if concurrent:
            self._links_counter = ThreadSafeCounter()
            self._followed_counter = ThreadSafeCounter()
            self._urls_safe = ThreadSafeList[str]()
            self._visited = ThreadSafeSet[str]()
            self._lock = threading.Lock()
        else:
            self._links: int = 0
            self._followed: int = 0
            self._urls: list[str] = []

    @property
    def links(self) -> int:
        """Get the number of links found."""
        if self.concurrent:
            return self._links_counter.value
        return self._links

    @links.setter
    def links(self, value: int) -> None:
        """Set the links counter."""
        if self.concurrent:
            with self._lock:
                self._links_counter._value = value
        else:
            self._links = value

    @property
    def followed(self) -> int:
        """Get the number of pages followed."""
        if self.concurrent:
            return self._followed_counter.value
        return self._followed

    @followed.setter
    def followed(self, value: int) -> None:
        """Set the followed counter."""
        if self.concurrent:
            with self._lock:
                self._followed_counter._value = value
        else:
            self._followed = value

    @property
    def urls(self) -> list[str]:
        """Get the list of discovered URLs."""
        if self.concurrent:
            return self._urls_safe.to_list()
        return self._urls

    @urls.setter
    def urls(self, value: list[str]) -> None:
        """Set the URLs list."""
        if self.concurrent:
            with self._lock:
                self._urls_safe = ThreadSafeList[str]()
                self._urls_safe.extend(value)
        else:
            self._urls = value

    def crawl(self) -> None:
        """Crawl the web starting from root URL.

        This method crawls URLs breadth-first up to the specified depth,
        collecting all discovered links. Uses concurrent mode if enabled.
        """
        if self.concurrent:
            self._crawl_concurrent()
        else:
            self._crawl_sequential()

    def _crawl_sequential(self) -> None:
        """Sequential crawling implementation (original behavior)."""
        page = Linkfetcher(self.root, browser=self.browser)
        page.linkfetch()
        url_queue: deque[str] = deque()
        for url in page.urls:
            url_queue.append(url)
        followed: list[str] = [self.root]
        n = 0

        while True:
            try:
                url = url_queue.pop()
                n += 1
                if url not in followed:
                    try:
                        host = urllib.parse.urlparse(url)[1]
                        if self.locked and re.match(f".*{self.host}", host):
                            followed.append(url)
                            self._followed += 1
                            page = Linkfetcher(url, browser=self.browser)
                            page.linkfetch()
                            for link in page:
                                if link not in self._urls:
                                    self._links += 1
                                    url_queue.append(link)
                                    self._urls.append(link)
                            if n > self.depth > 0:
                                break
                    except Exception as e:
                        print("Exception")
                        print(f"ERROR: The URL {url} can't be crawled {e}")
                        print(format_exc())
            except IndexError:
                break

    def _fetch_url(self, url: str) -> list[str]:
        """Fetch links from a single URL (used in concurrent mode).

        Args:
            url: The URL to fetch links from.

        Returns:
            List of discovered URLs.
        """
        try:
            page = Linkfetcher(url, browser=self.browser, thread_safe=True)
            page.linkfetch()
            return page.urls
        except Exception as e:
            print(f"ERROR: The URL {url} can't be crawled {e}")
            return []

    def _crawl_concurrent(self) -> None:
        """Concurrent crawling implementation using thread pool.

        This method takes advantage of free-threaded Python for true
        parallelism when the GIL is disabled.
        """
        # Initialize with root URL
        page = Linkfetcher(self.root, browser=self.browser, thread_safe=True)
        page.linkfetch()

        # Use thread-safe queue for URL frontier
        url_queue: queue.Queue[tuple[str, int]] = queue.Queue()
        for url in page.urls:
            url_queue.put((url, 0))  # (url, depth_level)

        # Mark root as visited
        self._visited.add(self.root)

        # Calculate optimal worker count
        initial_count = url_queue.qsize()
        workers = self.max_workers or get_optimal_worker_count(
            max(initial_count, 10), io_bound=True
        )

        with ThreadPoolExecutor(max_workers=workers) as executor:
            pending_futures: dict[Future[list[str]], str] = {}
            current_depth = 0

            while not url_queue.empty() or pending_futures:
                # Submit new tasks from queue
                while not url_queue.empty() and len(pending_futures) < workers * 2:
                    try:
                        url, depth = url_queue.get_nowait()
                    except queue.Empty:
                        break

                    # Check depth limit
                    if self.depth > 0 and depth > self.depth:
                        continue

                    # Skip if already visited
                    if not self._visited.add(url):
                        continue

                    # Check host lock
                    host = urllib.parse.urlparse(url)[1]
                    if self.locked and not re.match(f".*{self.host}", host):
                        continue

                    # Submit fetch task
                    future = executor.submit(self._fetch_url, url)
                    pending_futures[future] = url
                    self._followed_counter.increment()
                    current_depth = depth

                # Process completed futures
                if pending_futures:
                    done_futures = []
                    for future in list(pending_futures.keys()):
                        if future.done():
                            done_futures.append(future)

                    for future in done_futures:
                        source_url = pending_futures.pop(future)
                        try:
                            discovered_urls = future.result()
                            for link in discovered_urls:
                                if link not in self._visited:
                                    self._links_counter.increment()
                                    self._urls_safe.append(link)
                                    url_queue.put((link, current_depth + 1))
                        except Exception as e:
                            print(f"ERROR processing {source_url}: {e}")

                    # Brief pause to prevent busy-waiting
                    if not done_futures:
                        threading.Event().wait(0.01)

    @staticmethod
    def is_free_threaded() -> bool:
        """Check if running on free-threaded Python.

        Returns:
            True if GIL is disabled (free-threaded Python).
        """
        return is_gil_disabled()
