import unittest
from webcrawler import Webcrawler

class TestCrawler(unittest.TestCase):
    def test_crawler(self):
        url = 'http://gotchacode.com'
        depth = 2
        crawler = Webcrawler(url, depth)
        crawler.crawl()
        assert(len(crawler.urls) > 0)

if __name__ == '__main__':
    unittest.main()
