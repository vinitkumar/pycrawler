# pycrawler

A simple Python web crawler written for Python 3.14+ (supports CPython and PyPy).

[![Ruff](https://img.shields.io/badge/linter-ruff-blue)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/type%20checker-ty-blue)](https://github.com/astral-sh/ty)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/)

## Installation

### Using uv (recommended)

```sh
uv venv
uv pip install -e .
```

### Using pip

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```sh
# Crawl a website to depth 5
python main.py -d5 http://example.com

# Only fetch links from target URL (no crawling)
python main.py --links http://example.com

# Show help
python main.py --help

# Show version
python main.py --version
```

## Example Output

```sh
100%|████████████████████████████████████████████████████████| 50/50 [00:00<00:00, 29200.11it/s]
100%|██████████████████████████████████████████████████████████| 9/9 [00:00<00:00, 22563.50it/s]
100%|██████████████████████████████████████████████████████████| 9/9 [00:00<00:00, 21375.28it/s]
100%|████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 22227.37it/s]
CRAWLER STARTED:
https://vinitkumar.me, will crawl upto depth 2
https://vinitkumar.me/
http://changer.nl
https://twitter.com/vinitkme
https://vinitkumar.me/about
https://vinitkumar.github.io/vinit_kumar.pdf
https://vinitkumar.me/values
https://github.com/vinitkumar
https://vinitkumar.me/2013-03-24-life-has-changed/
https://vinitkumar.me/2013-03-24-my-javascript-love/
https://vinitkumar.me/2013-03-27-twitter-like-app-in-nodejs/
http://twitter.com/vinitkme
https://vinitkumar.me/2013-04-07-first-flight-and-vacation-after-months/
====================================================================================================
Crawler Statistics
====================================================================================================
No of links Found: 12
No of followed:     3
Found all links after 0.54s
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

### Type Checking (ty)

```sh
uvx ty check
```

### Running Tests

```sh
python -m pytest test_crawler.py
```

## Requirements

- Python 3.14+ (CPython or PyPy)
- beautifulsoup4
- rich

## Issues

Create an issue here if you encounter a bug: [create-issue](https://github.com/vinitkumar/pycrawler/issues/new/choose)

## License

MIT License - see [LICENSE](LICENSE) for details.
