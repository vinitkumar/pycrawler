# pycrawler

[![Python package](https://github.com/vinitkumar/pycrawler/actions/workflows/test.yml/badge.svg)](https://github.com/vinitkumar/pycrawler/actions/workflows/test.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python web crawler with **free-threaded Python support** for true parallel execution. Built for Python 3.13+ with concurrent crawling capabilities that take full advantage of Python 3.14t (GIL disabled).

## Features

- **Free-threaded Python Support**: True parallel execution on Python 3.13t/3.14t with GIL disabled
- **Concurrent Crawling**: Thread pool-based concurrent mode for faster crawling
- **Multiple Browser User-Agents**: Chromium, Firefox, Brave, Safari, and Edge
- **Depth Control**: Configurable crawl depth with breadth-first traversal
- **Thread-safe Primitives**: Built-in `ThreadSafeCounter`, `ThreadSafeList`, and `ThreadSafeSet`
- **Cross-platform**: Tested on Ubuntu, macOS, and Windows
- **Modern Tooling**: Uses `uv` for fast dependency management, `ruff` for linting

## Requirements

- Python 3.13+ (CPython)
- beautifulsoup4 >= 4.14.3
- rich >= 14.2.0

## Installation

### Using uv (recommended)

```sh
uv venv
uv pip install -e .
```

### Using pip

```sh
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Usage

### Basic Crawling

```sh
# Crawl a website to depth 5
python main.py -d 5 http://example.com

# Crawl with default depth (30)
python main.py http://example.com
```

### Concurrent Mode

Enable concurrent crawling for faster performance, especially on free-threaded Python:

```sh
# Enable concurrent crawling (auto-detect worker count)
python main.py -c http://example.com

# Specify number of worker threads
python main.py -c -w 8 http://example.com
```

### Link Fetching Only

```sh
# Only fetch links from target URL (no recursive crawling)
python main.py --links http://example.com
```

### Browser User-Agent

```sh
# Use Firefox User-Agent
python main.py --browser firefox http://example.com

# Available browsers: chromium (default), firefox, brave, safari, edge
python main.py -b safari http://example.com
```

### Other Options

```sh
# Show help
python main.py --help

# Show version
python main.py --version
```

## CLI Reference

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--depth` | `-d` | Maximum crawl depth | 30 |
| `--links` | `-l` | Only fetch links (no crawling) | False |
| `--browser` | `-b` | Browser User-Agent | chromium |
| `--concurrent` | `-c` | Enable concurrent crawling | False |
| `--workers` | `-w` | Worker threads (concurrent mode) | auto |
| `--version` | `-v` | Show version | - |
| `--help` | `-h` | Show help message | - |

## Example Output

```
Running on free-threaded Python (GIL disabled)
Working... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
****************************************************************************************************
Execution took: 0.54s
****************************************************************************************************
CRAWLER STARTED:
https://example.com, will crawl upto depth 5
Using chromium User-Agent
Concurrent mode: enabled (workers: auto)
https://example.com/
https://example.com/about
https://example.com/contact
====================================================================================================
Crawler Statistics
====================================================================================================
No of links Found: 12
No of followed:     3
```

## Free-threaded Python

This crawler is designed to take advantage of [free-threaded Python](https://docs.python.org/3.14/whatsnew/3.13.html#free-threaded-cpython) (Python 3.13t/3.14t with GIL disabled) for true parallel execution.

### Checking GIL Status

```python
import sys
if hasattr(sys, '_is_gil_enabled'):
    print(f"GIL enabled: {sys._is_gil_enabled()}")
```

### Performance Benefits

- **With GIL disabled**: Multiple threads can execute Python bytecode simultaneously
- **I/O-bound crawling**: Significant speedup with concurrent mode
- **Optimal worker count**: Automatically calculated based on GIL status and CPU count

## Programmatic Usage

```python
from src.webcrawler import Webcrawler
from src.linkfetcher import Linkfetcher

# Sequential crawling
crawler = Webcrawler("https://example.com", depth=5)
crawler.crawl()
print(f"Found {crawler.links} links")

# Concurrent crawling
crawler = Webcrawler(
    "https://example.com",
    depth=5,
    concurrent=True,
    max_workers=8
)
crawler.crawl()

# Link fetching only
fetcher = Linkfetcher("https://example.com", browser="firefox")
fetcher.linkfetch()
for url in fetcher:
    print(url)
```

### Thread-safe Utilities

```python
from src.threading_utils import (
    ThreadSafeCounter,
    ThreadSafeList,
    ThreadSafeSet,
    is_gil_disabled,
    parallel_map,
)

# Check if running on free-threaded Python
if is_gil_disabled():
    print("True parallelism available!")

# Thread-safe counter
counter = ThreadSafeCounter()
counter.increment()

# Thread-safe collections
urls = ThreadSafeList[str]()
urls.append("https://example.com")

visited = ThreadSafeSet[str]()
visited.add("https://example.com")

# Parallel map
results = parallel_map(fetch_url, url_list, max_workers=16)
```

## Development

### Setup

```sh
uv venv
uv pip install -e ".[dev]"
```

### Linting (Ruff)

```sh
uvx ruff check
uvx ruff format
```

### Type Checking

```sh
uvx ty check
```

### Running Tests

```sh
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --tb=short
```

## Project Structure

```
pycrawler/
├── main.py                 # CLI entry point
├── src/
│   ├── __init__.py         # Version and logging config
│   ├── webcrawler.py       # Main crawler class
│   ├── linkfetcher.py      # Link fetching and parsing
│   └── threading_utils.py  # Thread-safe primitives
├── tests/
│   ├── test_webcrawler.py
│   ├── test_linkfetcher.py
│   ├── test_threading_utils.py
│   └── test_main.py
└── pyproject.toml
```

## CI/CD

Tests run on GitHub Actions across:
- **Operating Systems**: Ubuntu, macOS, Windows
- **Python Versions**: 3.13, 3.14, 3.14t (free-threaded)

## Issues

Found a bug? [Create an issue](https://github.com/vinitkumar/pycrawler/issues/new/choose)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Authors

- [Vinit Kumar](https://github.com/vinitkumar)
- [Rushi Balapure](https://github.com/RushiBalapure)
