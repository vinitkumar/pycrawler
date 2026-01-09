"""Version and logging configuration for pycrawler."""

import logging

__version__: str = "4.0.0"

LOGGER: logging.Logger = logging.getLogger(__name__)
HANDLER: logging.StreamHandler = logging.StreamHandler()  # type: ignore[type-arg]
FORMATTER: logging.Formatter = logging.Formatter("%(levelname)-8s %(message)s")
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)
