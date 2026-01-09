"""Tests for the webcrawler module."""

import unittest

from src.webcrawler import Webcrawler


class TestCrawler(unittest.TestCase):
    """Test cases for the Webcrawler class."""

    def test_crawler(self) -> None:
        """Test that crawler finds URLs from a given website."""
        url = "http://gotchacode.com"
        depth = 2
        crawler = Webcrawler(url, depth)
        crawler.crawl()
        self.assertGreater(len(crawler.urls), 0)


if __name__ == "__main__":
    unittest.main()
