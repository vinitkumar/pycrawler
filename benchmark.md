# Benchmarks

## Real-site link extraction

Benchmarked with `hyperfine` against the same command on every Python runtime
currently covered by CI:

```sh
hyperfine --warmup 3 --runs 20 \
  --command-name "Python 3.14" \
    '.venv-3.14/bin/python main.py --links https://www.python.org >/dev/null 2>&1' \
  --command-name "Python 3.15 beta" \
    '.venv-3.15/bin/python main.py --links https://www.python.org >/dev/null 2>&1' \
  --command-name "Python 3.14t free-threaded" \
    '.venv-3.14t/bin/python main.py --links https://www.python.org >/dev/null 2>&1'
```

The command fetches and parses the live Python.org homepage and extracts 136
links. Output is redirected so terminal rendering does not dominate the timing.

| Runtime | Mean | Min | Max | Relative |
|:---|---:|---:|---:|---:|
| Python 3.14.6 | 190.1 ms +/- 37.0 ms | 150.0 ms | 274.7 ms | 1.10 +/- 0.25 |
| Python 3.15.0b3 | 172.7 ms +/- 19.5 ms | 153.0 ms | 234.3 ms | 1.00 |
| Python 3.14.0 free-threaded | 186.8 ms +/- 40.2 ms | 156.8 ms | 324.1 ms | 1.08 +/- 0.26 |

## Summary

Python 3.15 beta was the fastest in this sample, but the spread is small:
about 8-10% faster than Python 3.14 and Python 3.14t. This benchmark is mostly
network and HTML parsing work, so free-threaded Python does not show a clear
advantage for this single-process, single-page command.

Repeated runs against `https://vinitkumar.me` initially succeeded, finding 17
links with `main.py -d 1`, but the site began returning `403 Forbidden` during
the larger `hyperfine` run. The recorded benchmark therefore uses
`https://www.python.org`, another real public website that continued returning
successful responses throughout the sample.

Environment:

- Machine: macOS 26.5.1, arm64
- Tool: hyperfine 1.20.0
- Runs: 20 measured runs per command, 3 warmups
- Dependency set: uv-managed project environment from `uv.lock`
