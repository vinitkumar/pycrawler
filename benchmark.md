# Benchmarks

## Real-site depth-5 crawl

Benchmarked with `hyperfine` against the same command on every Python runtime
currently covered by CI:

```sh
hyperfine --warmup 3 --runs 20 \
  --command-name "Python 3.14" \
    '.venv-3.14/bin/python main.py -d 5 https://lifehacker.com/ >/dev/null 2>&1' \
  --command-name "Python 3.15 beta" \
    '.venv-3.15/bin/python main.py -d 5 https://lifehacker.com/ >/dev/null 2>&1' \
  --command-name "Python 3.14t free-threaded" \
    '.venv-3.14t/bin/python main.py -d 5 https://lifehacker.com/ >/dev/null 2>&1'
```

The command fetches the live Lifehacker homepage and crawls to depth 5. In the
smoke run immediately before benchmarking, the crawler followed 1 page and
recorded 2 discovered links. Output is redirected so terminal rendering does not
dominate the timing.

| Runtime | Mean | Min | Max | Relative |
|:---|---:|---:|---:|---:|
| Python 3.14.6 | 470.4 ms +/- 122.6 ms | 338.7 ms | 822.1 ms | 1.10 +/- 0.35 |
| Python 3.15.0b3 | 426.0 ms +/- 76.9 ms | 328.5 ms | 630.0 ms | 1.00 |
| Python 3.14.0 free-threaded | 440.7 ms +/- 57.8 ms | 352.8 ms | 531.4 ms | 1.03 +/- 0.23 |

## Summary

Python 3.15.0b3 was the fastest in this Lifehacker depth-5 sample, with Python
3.14t about 3% slower and Python 3.14.6 about 10% slower. The variance is large
enough that the supported runtimes should be treated as broadly close for this
live network crawl. This benchmark is mostly HTTP fetches and HTML parsing, so
free-threaded Python does not show a clear advantage for this sequential
crawler command.

Repeated runs against `https://vinitkumar.me` initially succeeded, finding 17
links with `main.py -d 1`, but the site began returning no crawlable links
during repeated benchmark runs. The recorded benchmark therefore uses
`https://lifehacker.com/`, a real public website that continued returning
successful responses throughout the sample.

Environment:

- Machine: macOS 26.5.1, arm64
- Tool: hyperfine 1.20.0
- Runs: 20 measured runs per command, 3 warmups
- Dependency set: uv-managed project environment from `uv.lock`
