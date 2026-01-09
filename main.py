"""Main Entry Point for the crawler."""

from __future__ import annotations

import argparse
import time
from functools import wraps
from typing import TYPE_CHECKING

from src import LOGGER, __version__
from src.linkfetcher import Linkfetcher
from src.webcrawler import Webcrawler

if TYPE_CHECKING:
    from collections.abc import Callable


def timethis[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to measure execution time of a function."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print("*" * 100)
        print(f"Execution took: {end - start}s")
        print("*" * 100)
        return result

    return wrapper


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="A simple Python web crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s -d5 http://example.com
        Crawl example.com to a depth of 5

    %(prog)s --links http://example.com
        Only fetch links from the target URL
        """,
    )

    parser.add_argument(
        "url",
        help="Target URL to start crawling",
    )

    parser.add_argument(
        "-l",
        "--links",
        action="store_true",
        default=False,
        help="Only fetch links for target URL (don't crawl)",
    )

    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=30,
        help="Maximum depth to traverse (default: 30)",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser.parse_args()


def getlinks(url: str) -> list[tuple[int, str]]:
    """Get links from the Linkfetcher class.

    Args:
        url: The URL to fetch links from.

    Returns:
        A list of tuples containing (index, url).
    """
    page = Linkfetcher(url)
    page.linkfetch()
    return [(i, url_link) for i, url_link in enumerate(page)]


@timethis
def crawl(url: str, depth: int) -> Webcrawler:
    """Crawl the given URL to the specified depth.

    Args:
        url: The starting URL.
        depth: Maximum crawl depth.

    Returns:
        The Webcrawler instance with results.
    """
    webcrawler = Webcrawler(url, depth)
    webcrawler.crawl()
    return webcrawler


def main() -> None:
    """Main entry point for the crawler."""
    args = parse_args()
    url = args.url

    if args.links:
        links = getlinks(url)
        for i, link in links:
            LOGGER.info("Link %d: %s", i, link)
        raise SystemExit(0)

    depth = args.depth

    webcrawler = crawl(url, depth)
    print("CRAWLER STARTED:")
    print(f"{url}, will crawl upto depth {depth}")
    print("\n".join(webcrawler.urls))
    print("=" * 100)
    print("Crawler Statistics")
    print("=" * 100)
    print(f"No of links Found: {webcrawler.links}")
    print(f"No of followed:     {webcrawler.followed}")


if __name__ == "__main__":
    main()
