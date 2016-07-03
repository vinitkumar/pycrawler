#!/usr/bin/python
import asyncio
import time
import optparse
from linkfetcher import Linkfetcher
from webcrawler import Webcrawler
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def option_parser():
    """Option Parser to give various options."""
    usage = '''
             $ ./crawler -d5 <url>
                Here in this case it goes till depth of 5 and url is target URL to
                start crawling.
            '''
    version = "2.0.0"

    parser = optparse.OptionParser(usage=usage, version=version)

    parser.add_option("-l", "--links", action="store_true",
                      default=False, dest="links", help="links for target url")

    parser.add_option("-d", "--depth", action="store", type="int",
                      default=30, dest="depth", help="Maximum depth traverse")
    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    return opts, args


async def getlinks(url):
    """Get Links from the Linkfetcher class."""
    page = Linkfetcher(url)
    await page.linkfetch()
    for i, url in enumerate(page):
        return (i, url)


async def main():
    """ Main class."""
    opts, args = option_parser()
    url = args[0]

    if opts.links:
        getlinks(url)
        raise SystemExit(0)

    depth = opts.depth

    sTime = time.time()
    webcrawler = Webcrawler(url, depth)
    webcrawler.crawl()
    eTime = time.time()
    tTime = eTime - sTime
    logger.info("CRAWLER STARTED:")
    logger.info("%s, will crawl upto depth %d" % (url, depth))
    logger.info("*****RESULTS")
    logger.info("\n".join(webcrawler.urls))
    logger.info("=" * 100)
    logger.info("Crawler Statistics")
    logger.info("=" * 100)
    logger.info("No of links Found: %d" % webcrawler.links)
    logger.info("No of followed:     %d" % webcrawler.followed)
    logger.info("Time Stats : Found all links  after %0.2fs" % tTime)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
