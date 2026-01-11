"""Threading utilities for free-threaded Python support.

This module provides utilities for detecting and working with free-threaded
Python (Python 3.13+ built with --disable-gil), as well as thread-safe
primitives for concurrent operations.
"""

from __future__ import annotations

import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable
    from concurrent.futures import Future

T = TypeVar("T")


def is_gil_disabled() -> bool:
    """Check if the GIL is disabled (free-threaded Python).

    Returns:
        True if running on free-threaded Python with GIL disabled.
    """
    # Python 3.13+ provides sys._is_gil_enabled()
    if hasattr(sys, "_is_gil_enabled"):
        return not sys._is_gil_enabled()
    return False


def get_python_build_info() -> dict[str, bool | str]:
    """Get information about the Python build configuration.

    Returns:
        Dictionary with build information including GIL status.
    """
    return {
        "version": sys.version,
        "gil_disabled": is_gil_disabled(),
        "free_threaded": is_gil_disabled(),
        "thread_safe_refcounting": is_gil_disabled(),
    }


@dataclass
class ThreadSafeCounter:
    """A thread-safe counter for tracking progress in concurrent operations."""

    _value: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def increment(self, amount: int = 1) -> int:
        """Increment the counter and return the new value."""
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        """Decrement the counter and return the new value."""
        with self._lock:
            self._value -= amount
            return self._value

    @property
    def value(self) -> int:
        """Get the current counter value."""
        with self._lock:
            return self._value


@dataclass
class ThreadSafeSet[T]:
    """A thread-safe set implementation for tracking visited URLs."""

    _data: set[T] = field(default_factory=set)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add(self, item: T) -> bool:
        """Add an item to the set.

        Returns:
            True if the item was added (not already present), False otherwise.
        """
        with self._lock:
            if item in self._data:
                return False
            self._data.add(item)
            return True

    def contains(self, item: T) -> bool:
        """Check if an item is in the set."""
        with self._lock:
            return item in self._data

    def __contains__(self, item: T) -> bool:
        """Support 'in' operator."""
        return self.contains(item)

    def __len__(self) -> int:
        """Return the number of items in the set."""
        with self._lock:
            return len(self._data)

    def to_list(self) -> list[T]:
        """Return a copy of the set as a list."""
        with self._lock:
            return list(self._data)


@dataclass
class ThreadSafeList[T]:
    """A thread-safe list implementation for collecting results."""

    _data: list[T] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def append(self, item: T) -> None:
        """Append an item to the list."""
        with self._lock:
            self._data.append(item)

    def extend(self, items: list[T]) -> None:
        """Extend the list with multiple items."""
        with self._lock:
            self._data.extend(items)

    def __len__(self) -> int:
        """Return the number of items in the list."""
        with self._lock:
            return len(self._data)

    def __iter__(self):
        """Iterate over a copy of the list."""
        with self._lock:
            return iter(list(self._data))

    def to_list(self) -> list[T]:
        """Return a copy of the list."""
        with self._lock:
            return list(self._data)


def parallel_map[T, R](
    func: Callable[[T], R],
    items: list[T],
    max_workers: int | None = None,
    *,
    timeout: float | None = None,
) -> list[R]:
    """Execute a function in parallel over a list of items.

    This function takes advantage of free-threaded Python for true parallelism
    when available, while still working correctly with the GIL enabled.

    Args:
        func: The function to execute for each item.
        items: List of items to process.
        max_workers: Maximum number of worker threads. Defaults to min(32, len(items) + 4).
        timeout: Optional timeout for each task.

    Returns:
        List of results in the same order as the input items.
    """
    if not items:
        return []

    # Use more workers when GIL is disabled for better parallelism
    if max_workers is None:
        if is_gil_disabled():
            max_workers = min(64, len(items), (len(items) + 4))
        else:
            max_workers = min(32, len(items), (len(items) + 4))

    results: list[R] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures: dict[Future[R], int] = {
            executor.submit(func, item): i for i, item in enumerate(items)
        }

        # Pre-allocate results list
        results = [None] * len(items)  # type: ignore[list-item]

        for future in as_completed(futures, timeout=timeout):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception:
                # Store None for failed operations
                results[idx] = None  # type: ignore[assignment]

    return results


def get_optimal_worker_count(task_count: int, io_bound: bool = True) -> int:
    """Calculate optimal number of workers based on task characteristics.

    Args:
        task_count: Number of tasks to execute.
        io_bound: Whether tasks are I/O bound (True) or CPU bound (False).

    Returns:
        Optimal number of worker threads.
    """
    import os

    cpu_count = os.cpu_count() or 4

    if is_gil_disabled():
        # With GIL disabled, we can use more threads for both I/O and CPU tasks
        if io_bound:
            # I/O bound tasks can use many threads
            return min(task_count, cpu_count * 8, 128)
        # CPU bound tasks benefit from ~CPU count threads
        return min(task_count, cpu_count * 2)
    # With GIL, threads help mainly for I/O bound tasks
    if io_bound:
        return min(task_count, cpu_count * 4, 64)
    # CPU bound tasks don't benefit much from threads with GIL
    return min(task_count, cpu_count)
