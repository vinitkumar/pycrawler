from .webcrawler import Webcrawler


def test_crawler():
    url = 'http://gotchacode.com'
    depth = 2
    crawler = Webcrawler(url, depth)
    crawler.crawl()
    assert(len(crawler.urls) > 0)

