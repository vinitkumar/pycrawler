#! /usr/bin/env python
import time
import optparse
from linkfetcher import Linkfetcher
from webcrawler import Webcrawler

Usage = '''
 $ ./crawler -d5 <url>
    Here in this case it goes till depth of 5 and url is target URL to
    start crawling.
'''
Version = '0.0.1'


def option_parser():

    parser = optparse.OptionParser(usage=Usage, version=Version)

    parser.add_option("-l", "--links", action="store_true",
        default=False,dest="links", help="Get links for target url only")

    parser.add_option("-d", "--depth", action="store", type="int" ,
        default=30, dest="depth", help="Maximum depth to traverse")
    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1

    return opts, args


def getlinks(url):
    page = Linkfetcher(url)
    page.linkfetch()
    for i, url in enumerate(page):
        print "%d ==> %s" % (i, url)


def main():

    opts, args = option_parser()
    url = args[0]

    if opts.links:
        getlinks(url)
        raise SystemExit, 0

    depth = opts.depth

    sTime = time.time()

    print "Crawler started for %s, will crawl upto depth %d" %(url, depth)
    print "==============================================================="
    webcrawler = Webcrawler(url, depth)
    webcrawler.crawl()
    print "\n".join(webcrawler.urls)

    eTime = time.time()
    tTime = eTime - sTime
    print "\n"
    print "Crawler Statistics"
    print "=================="
    print "No of links Found: %d" % webcrawler.links
    print "No of follwed:     %d" % webcrawler.followed
    print "Time Stats : Found all links  after %0.2fs" % tTime


if __name__ == "__main__":
    main()
