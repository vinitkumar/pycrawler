"""
Main Entry Point for the crawler
"""
#! /usr/bin/python
import asyncio
import time
import optparse
import logging
from src.linkfetcher import Linkfetcher
from src.webcrawler import Webcrawler
from src import __version__, LOGGER


def option_parser():
    """Option Parser to give various options."""
    usage = """
             $ ./crawler -d5 <url>
                Here in this case it goes till depth of 5 and url is target URL to
                start crawling.
            """
    version = __version__

    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option(
        "-l",
        "--links",
        action="store_true",
        default=False,
        dest="links",
        help="links for target url",
    )

    parser.add_option(
        "-d",
        "--depth",
        action="store",
        type="int",
        default=30,
        dest="depth",
        help="Maximum depth traverse",
    )
    opts, args = parser.parse_args()

    if not args:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


async def getlinks(url):
    """Get Links from the Linkfetcher class."""
    page = Linkfetcher(url)
    await page.linkfetch()
    for i, url_link in enumerate(page):
        return (i, url_link)


async def main():
    """ Main class."""
    opts, args = option_parser()
    url = args[0]

    if opts.links:
        await getlinks(url)
        raise SystemExit(0)

    depth = opts.depth

    s_time = time.time()
    webcrawler = Webcrawler(url, depth)
    webcrawler.crawl()
    e_time = time.time()
    t_time = e_time - s_time
    print("CRAWLER STARTED:")
    print("%s, will crawl upto depth %d" % (url, depth))
    print("\n".join(webcrawler.urls))
    print("=" * 100)
    print("Crawler Statistics")
    print("=" * 100)
    print("No of links Found: %d" % webcrawler.links)
    print("No of followed:     %d" % webcrawler.followed)
    print("Found all links after %0.2fs" % t_time)


if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main())
