import unittest
from src.webcrawler import Webcrawler

class TestCrawler(unittest.TestCase):
    def test_crawler(self):
        url = 'http://gotchacode.com'
        depth = 2
        crawler = Webcrawler(url, depth)
        crawler.crawl()
        self.assertTrue(len(crawler.urls) > 0, True)

if __name__ == '__main__':
    unittest.main()
