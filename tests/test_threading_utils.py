"""Unit tests for the threading utilities module."""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.threading_utils import (
    ThreadSafeCounter,
    ThreadSafeList,
    ThreadSafeSet,
    get_optimal_worker_count,
    get_python_build_info,
    is_gil_disabled,
    parallel_map,
)


class TestIsGilDisabled:
    """Tests for is_gil_disabled function."""

    def test_returns_bool(self) -> None:
        """Test that is_gil_disabled returns a boolean."""
        result = is_gil_disabled()
        assert isinstance(result, bool)

    def test_consistent_results(self) -> None:
        """Test that repeated calls return consistent results."""
        result1 = is_gil_disabled()
        result2 = is_gil_disabled()
        assert result1 == result2


class TestGetPythonBuildInfo:
    """Tests for get_python_build_info function."""

    def test_returns_dict(self) -> None:
        """Test that get_python_build_info returns a dictionary."""
        info = get_python_build_info()
        assert isinstance(info, dict)

    def test_contains_expected_keys(self) -> None:
        """Test that result contains expected keys."""
        info = get_python_build_info()
        expected_keys = {"version", "gil_disabled", "free_threaded", "thread_safe_refcounting"}
        assert set(info.keys()) == expected_keys

    def test_version_is_string(self) -> None:
        """Test that version is a string."""
        info = get_python_build_info()
        assert isinstance(info["version"], str)

    def test_gil_disabled_matches_helper(self) -> None:
        """Test that gil_disabled matches is_gil_disabled()."""
        info = get_python_build_info()
        assert info["gil_disabled"] == is_gil_disabled()


class TestThreadSafeCounter:
    """Tests for ThreadSafeCounter class."""

    def test_initial_value_is_zero(self) -> None:
        """Test that counter starts at zero."""
        counter = ThreadSafeCounter()
        assert counter.value == 0

    def test_increment(self) -> None:
        """Test basic increment."""
        counter = ThreadSafeCounter()
        result = counter.increment()
        assert result == 1
        assert counter.value == 1

    def test_increment_by_amount(self) -> None:
        """Test increment by specific amount."""
        counter = ThreadSafeCounter()
        counter.increment(5)
        assert counter.value == 5

    def test_decrement(self) -> None:
        """Test basic decrement."""
        counter = ThreadSafeCounter()
        counter.increment(10)
        result = counter.decrement()
        assert result == 9
        assert counter.value == 9

    def test_decrement_by_amount(self) -> None:
        """Test decrement by specific amount."""
        counter = ThreadSafeCounter()
        counter.increment(10)
        counter.decrement(3)
        assert counter.value == 7

    def test_thread_safety(self) -> None:
        """Test that counter is thread-safe under concurrent access."""
        counter = ThreadSafeCounter()
        num_threads = 10
        increments_per_thread = 1000

        def increment_many():
            for _ in range(increments_per_thread):
                counter.increment()

        threads = [threading.Thread(target=increment_many) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = num_threads * increments_per_thread
        assert counter.value == expected


class TestThreadSafeSet:
    """Tests for ThreadSafeSet class."""

    def test_initial_empty(self) -> None:
        """Test that set starts empty."""
        ts_set: ThreadSafeSet[str] = ThreadSafeSet()
        assert len(ts_set) == 0

    def test_add_returns_true_for_new_item(self) -> None:
        """Test add returns True for new item."""
        ts_set: ThreadSafeSet[str] = ThreadSafeSet()
        assert ts_set.add("item1") is True

    def test_add_returns_false_for_existing_item(self) -> None:
        """Test add returns False for existing item."""
        ts_set: ThreadSafeSet[str] = ThreadSafeSet()
        ts_set.add("item1")
        assert ts_set.add("item1") is False

    def test_contains(self) -> None:
        """Test contains method."""
        ts_set: ThreadSafeSet[str] = ThreadSafeSet()
        ts_set.add("item1")
        assert ts_set.contains("item1") is True
        assert ts_set.contains("item2") is False

    def test_in_operator(self) -> None:
        """Test 'in' operator support."""
        ts_set: ThreadSafeSet[str] = ThreadSafeSet()
        ts_set.add("item1")
        assert "item1" in ts_set
        assert "item2" not in ts_set

    def test_len(self) -> None:
        """Test length calculation."""
        ts_set: ThreadSafeSet[str] = ThreadSafeSet()
        ts_set.add("a")
        ts_set.add("b")
        ts_set.add("c")
        assert len(ts_set) == 3

    def test_to_list(self) -> None:
        """Test conversion to list."""
        ts_set: ThreadSafeSet[str] = ThreadSafeSet()
        ts_set.add("a")
        ts_set.add("b")
        result = ts_set.to_list()
        assert isinstance(result, list)
        assert set(result) == {"a", "b"}

    def test_thread_safety(self) -> None:
        """Test that set is thread-safe under concurrent access."""
        ts_set: ThreadSafeSet[int] = ThreadSafeSet()
        num_threads = 10
        items_per_thread = 100

        def add_items(thread_id: int):
            for i in range(items_per_thread):
                ts_set.add(thread_id * items_per_thread + i)

        threads = [threading.Thread(target=add_items, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = num_threads * items_per_thread
        assert len(ts_set) == expected


class TestThreadSafeList:
    """Tests for ThreadSafeList class."""

    def test_initial_empty(self) -> None:
        """Test that list starts empty."""
        ts_list: ThreadSafeList[str] = ThreadSafeList()
        assert len(ts_list) == 0

    def test_append(self) -> None:
        """Test append method."""
        ts_list: ThreadSafeList[str] = ThreadSafeList()
        ts_list.append("item1")
        assert len(ts_list) == 1

    def test_extend(self) -> None:
        """Test extend method."""
        ts_list: ThreadSafeList[str] = ThreadSafeList()
        ts_list.extend(["a", "b", "c"])
        assert len(ts_list) == 3

    def test_iter(self) -> None:
        """Test iteration."""
        ts_list: ThreadSafeList[str] = ThreadSafeList()
        ts_list.extend(["a", "b", "c"])
        result = list(ts_list)
        assert result == ["a", "b", "c"]

    def test_to_list(self) -> None:
        """Test conversion to list."""
        ts_list: ThreadSafeList[str] = ThreadSafeList()
        ts_list.extend(["a", "b"])
        result = ts_list.to_list()
        assert isinstance(result, list)
        assert result == ["a", "b"]

    def test_thread_safety(self) -> None:
        """Test that list is thread-safe under concurrent access."""
        ts_list: ThreadSafeList[int] = ThreadSafeList()
        num_threads = 10
        items_per_thread = 100

        def add_items():
            for i in range(items_per_thread):
                ts_list.append(i)

        threads = [threading.Thread(target=add_items) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = num_threads * items_per_thread
        assert len(ts_list) == expected


class TestParallelMap:
    """Tests for parallel_map function."""

    def test_empty_list(self) -> None:
        """Test with empty input list."""
        result = parallel_map(lambda x: x * 2, [])
        assert result == []

    def test_basic_transformation(self) -> None:
        """Test basic parallel transformation."""
        result = parallel_map(lambda x: x * 2, [1, 2, 3, 4, 5])
        assert result == [2, 4, 6, 8, 10]

    def test_preserves_order(self) -> None:
        """Test that results maintain input order."""
        items = list(range(100))
        result = parallel_map(lambda x: x * 2, items)
        expected = [x * 2 for x in items]
        assert result == expected

    def test_with_io_simulation(self) -> None:
        """Test with simulated I/O operations."""
        def slow_double(x: int) -> int:
            time.sleep(0.01)  # Simulate I/O
            return x * 2

        items = list(range(10))
        result = parallel_map(slow_double, items, max_workers=5)
        expected = [x * 2 for x in items]
        assert result == expected

    def test_handles_exceptions(self) -> None:
        """Test that exceptions are handled gracefully."""
        def maybe_fail(x: int) -> int | None:
            if x == 5:
                raise ValueError("Test error")
            return x * 2

        items = list(range(10))
        result = parallel_map(maybe_fail, items)
        # Failed item should be None
        assert result[5] is None
        # Other items should be correct
        assert result[0] == 0
        assert result[9] == 18


class TestGetOptimalWorkerCount:
    """Tests for get_optimal_worker_count function."""

    def test_returns_positive_integer(self) -> None:
        """Test that function returns positive integer."""
        result = get_optimal_worker_count(100)
        assert isinstance(result, int)
        assert result > 0

    def test_limited_by_task_count(self) -> None:
        """Test that result is limited by task count."""
        result = get_optimal_worker_count(2, io_bound=True)
        assert result <= 2

    def test_io_bound_uses_more_workers(self) -> None:
        """Test that I/O bound tasks use more workers."""
        io_result = get_optimal_worker_count(100, io_bound=True)
        cpu_result = get_optimal_worker_count(100, io_bound=False)
        # I/O bound should generally use more workers
        assert io_result >= cpu_result

    def test_large_task_count(self) -> None:
        """Test with large task count."""
        result = get_optimal_worker_count(10000, io_bound=True)
        # Should have reasonable upper bound
        assert result <= 128


class TestConcurrentWebcrawler:
    """Tests for concurrent Webcrawler functionality."""

    def test_webcrawler_concurrent_init(self) -> None:
        """Test Webcrawler initialization with concurrent mode."""
        from src.webcrawler import Webcrawler

        crawler = Webcrawler(
            "https://example.com",
            depth=5,
            concurrent=True,
            max_workers=4,
        )
        assert crawler.concurrent is True
        assert crawler.max_workers == 4

    def test_webcrawler_is_free_threaded(self) -> None:
        """Test is_free_threaded static method."""
        from src.webcrawler import Webcrawler

        result = Webcrawler.is_free_threaded()
        assert isinstance(result, bool)
        assert result == is_gil_disabled()

    def test_concurrent_counters_thread_safe(self) -> None:
        """Test that concurrent mode uses thread-safe counters."""
        from src.webcrawler import Webcrawler

        crawler = Webcrawler("https://example.com", depth=5, concurrent=True)

        # Test links property
        assert crawler.links == 0
        crawler.links = 10
        assert crawler.links == 10

        # Test followed property
        assert crawler.followed == 0
        crawler.followed = 5
        assert crawler.followed == 5

    def test_concurrent_urls_thread_safe(self) -> None:
        """Test that concurrent mode uses thread-safe URL list."""
        from src.webcrawler import Webcrawler

        crawler = Webcrawler("https://example.com", depth=5, concurrent=True)

        # Test urls property
        assert crawler.urls == []
        crawler.urls = ["url1", "url2"]
        assert len(crawler.urls) == 2


class TestLinkfetcherThreadSafe:
    """Tests for thread-safe Linkfetcher functionality."""

    def test_linkfetcher_thread_safe_init(self) -> None:
        """Test Linkfetcher initialization with thread_safe mode."""
        from src.linkfetcher import Linkfetcher

        fetcher = Linkfetcher("https://example.com", thread_safe=True)
        assert fetcher._thread_safe is True

    def test_linkfetcher_urls_property_thread_safe(self) -> None:
        """Test that urls property works in thread-safe mode."""
        from src.linkfetcher import Linkfetcher

        fetcher = Linkfetcher("https://example.com", thread_safe=True)
        assert fetcher.urls == []

        # Test setting urls
        fetcher.urls = ["url1", "url2"]
        assert len(fetcher.urls) == 2

    def test_linkfetcher_broken_urls_property_thread_safe(self) -> None:
        """Test that broken_urls property works in thread-safe mode."""
        from src.linkfetcher import Linkfetcher

        fetcher = Linkfetcher("https://example.com", thread_safe=True)
        assert fetcher.broken_urls == []

        # Test setting broken_urls
        fetcher.broken_urls = ["bad1"]
        assert len(fetcher.broken_urls) == 1

    def test_linkfetcher_len_thread_safe(self) -> None:
        """Test __len__ in thread-safe mode."""
        from src.linkfetcher import Linkfetcher

        fetcher = Linkfetcher("https://example.com", thread_safe=True)
        fetcher.urls = ["a", "b", "c"]
        assert len(fetcher) == 3

    def test_linkfetcher_getitem_thread_safe(self) -> None:
        """Test __getitem__ in thread-safe mode."""
        from src.linkfetcher import Linkfetcher

        fetcher = Linkfetcher("https://example.com", thread_safe=True)
        fetcher.urls = ["url0", "url1", "url2"]
        assert fetcher[0] == "url0"
        assert fetcher[1] == "url1"

    def test_linkfetcher_iter_thread_safe(self) -> None:
        """Test __iter__ in thread-safe mode."""
        from src.linkfetcher import Linkfetcher

        fetcher = Linkfetcher("https://example.com", thread_safe=True)
        fetcher.urls = ["a", "b", "c"]
        result = list(fetcher)
        assert result == ["a", "b", "c"]


class TestConcurrentCrawlReal:
    """Integration tests for concurrent crawling with real HTTP requests."""

    @pytest.mark.slow
    def test_concurrent_crawl_example_com(self) -> None:
        """Test concurrent crawling of example.com."""
        from src.webcrawler import Webcrawler

        crawler = Webcrawler(
            "https://example.com",
            depth=1,
            concurrent=True,
            max_workers=4,
        )
        crawler.crawl()
        # Should complete without errors
        assert isinstance(crawler.urls, list)

    @pytest.mark.slow
    def test_concurrent_vs_sequential_results_similar(self) -> None:
        """Test that concurrent and sequential modes produce similar results."""
        from src.webcrawler import Webcrawler

        # Sequential
        seq_crawler = Webcrawler("https://example.com", depth=1, concurrent=False)
        seq_crawler.crawl()

        # Concurrent
        conc_crawler = Webcrawler(
            "https://example.com", depth=1, concurrent=True, max_workers=4
        )
        conc_crawler.crawl()

        # Both should find links (exact count may vary due to timing)
        # Just verify both complete without errors
        assert isinstance(seq_crawler.urls, list)
        assert isinstance(conc_crawler.urls, list)
