"""Version and logging configuration for pycrawler."""

import logging

from src.threading_utils import (
    ThreadSafeCounter,
    ThreadSafeList,
    ThreadSafeSet,
    get_optimal_worker_count,
    get_python_build_info,
    is_gil_disabled,
    parallel_map,
)

__version__: str = "4.1.0"

LOGGER: logging.Logger = logging.getLogger(__name__)
HANDLER: logging.StreamHandler = logging.StreamHandler()
FORMATTER: logging.Formatter = logging.Formatter("%(levelname)-8s %(message)s")
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)

# Re-export threading utilities for convenience

__all__ = [
    "LOGGER",
    "ThreadSafeCounter",
    "ThreadSafeList",
    "ThreadSafeSet",
    "__version__",
    "get_optimal_worker_count",
    "get_python_build_info",
    "is_gil_disabled",
    "parallel_map",
]
