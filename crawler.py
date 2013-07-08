#! /usr/bin/env python

import sys,re,time,math,urllib2,optparse,urlparse
from BeautifulSoup import BeautifulSoup
from traceback import format_exc
from cgi import escape
from Queue import Queue, Empty as QueueEmpty

__author__="Vinit Kumar"
__version__  = "0.1"
__license__ ="MIT"
Version="0.1"
Usage="""

This crawler starts with a target url, fetches the web-page of that url
and parser all the links  of that page and stores it in a repo. Next it
uses the url from the  repo  and repears the same process.This process
goes on till a respective number of links are fetched or if it reaches
its depth.

In Order to use:
    $ ./crawler -d5 <url>
    Here in this case it goes till depth of 5 and url is target URL to
    start crawling.

"""
Agent = "%s/%s" % (__name__,__version__)

class Webcrawler(object):

    def __init__(self, root, depth, locked=True):
        self.root = root  #start of the crawling
        self.depth = depth  #depth upto which it traverse
        self.locked = locked
        self.links = 0
        self.followed = 0
        self.urls = []  #the Repo
        self.host = urlparse.urlparse(root)[1]


    def crawl(self):
        """"
        This function fetches all links of the page and arranges in a
        queue.Now urls take one by one and crawling operation is performed
        """

        page = Linkfetcher(self.root)
        page.linkfetch()
        queue = Queue()
        for url in page.urls:
            queue.put(url)
        followed = [self.root]

        n = 0

        while True:
            try:
                url = queue.get()
            except QueueEmpty:
                break

            n += 1 #this controls the crawler to run upto specified depth

            if url not in followed:
                try:

                    host = urlparse.urlparse(url)[1]

                    if self.locked and re.match(".*%s" % self.host, host):
                        followed.append(url)
                        self.followed += 1
                        page = Linkfetcher(url)
                        page.linkfetch()
                        for i, url in enumerate(page):
                            if url not in self.urls:
                                self.links += 1
                                queue.put(url)
                                self.urls.append(url)

                        if n > self.depth and self.depth > 0:
                            break
                except Exception, e:
                    print "ERROR: The URL '%s' can't be processed due to (%s)" % (url, e)
                    print format_exc()






class Linkfetcher(object):
    """This class as its name suggest fetches the links
    """

    def __init__(self, url):
        self.url = url
        self.urls = []

    def _addHeaders(self, request):
        request.add_header("User-Agent", Agent)

    def __getitem__(self, x):
        return self.urls[x]

    def open(self):

        url = self.url
        try:
            request = urllib2.Request(url)
            handle = urllib2.build_opener()
        except IOError:
            return None
        return (request, handle)



    def linkfetch(self):

        request, handle = self.open()
        self._addHeaders(request)
        if handle:
            try:
                content = unicode(handle.open(request).read(), "utf-8",
                        errors="replace")
                soup = BeautifulSoup(content)
                tags = soup('a')
            except urllib2.HTTPError, error:

                if error.code == 404:
                    print >> sys.stderr,"ERROR: %s -> %s" % (error,error.url)
                else:
                    print >> sys.stderr,"ERROR: %s" % error
                tags = []

            except urllib2.URLError, error:
                print >> sys.stderr, "ERROR: %s" % error
                tags=[]
            for tag in tags:
                href = tag.get("href")
                if href is not None:
                     url = urlparse.urljoin(self.url, escape(href))
                     if url not in self:
                         self.urls.append(url)





def option_parser():
#This gives a cleaner interface for taking option and arguments as compared to sys.argv[]

    parser = optparse.OptionParser(usage=Usage, version=Version)

    parser.add_option("-l","--links",
            action="store_true",default=False,dest="links",
            help="Get links for target url only")

    parser.add_option("-d","--depth",
            action="store", type="int" ,default=30, dest="depth",
            help="Maximum depth to traverse")
    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit, 1

    return opts, args




def getlinks(): #the function to get links
    page = Linkfetcher(url)
    page.linkfetch()
    for i, url in enumerate(page):
        print "%d ==> %s" % (i, url)



def main():

    opts, args = option_parser()

    url = args[0] #target url

    if opts.links:
        getlinks(url)
        raise SystemExit, 0

    depth = opts.depth

    sTime = time.time()   #start-time

    print "Crawler started for %s, will crawl upto depth %d" %(url, depth)
    print "==============================================================="
    webcrawler = Webcrawler(url,depth)
    webcrawler.crawl()
    print "\n".join(webcrawler.urls)

    eTime = time.time() # end-time
    tTime = eTime - sTime #time taken for crawling
    print "\n"
    print "Crawler Statistics"
    print "=================="
    print "No of links Found: %d" % webcrawler.links
    print "No of follwed:     %d" % webcrawler.followed
    print "Time Stats : Found all links  after %0.2fs" % tTime



if __name__ == "__main__":
    main()
