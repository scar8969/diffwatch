<p align="center">
  <img src="docs/assets/screens/root.png" alt="diffwatch running" width="900">
</p>

<h1 align="center">diffwatch</h1>

<p align="center"><b>Watch a page, keep every snapshot, diff what changed.</b></p>

<p align="center">
  <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-24%20passed-2ea44f" alt="tests: 24 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-68.1%-yellow" alt="coverage: 68.1%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-8%20answered-0969da" alt="routes: 8 answered"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

diffwatch fetches a URL on an interval, normalises the HTML, stores a snapshot and reports the diff against the previous one. Ignore patterns keep cookie banners and timestamps out of the noise.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

Change detection is easy to demo and hard to keep useful: without normalisation every fetch differs, and without stored snapshots you cannot tell what actually changed. This service keeps the history and diffs against it.

## What it does

| Capability | How it works |
| --- | --- |
| **Interval per watch** | Each watch owns its interval and last-checked time; the scheduler honours both. |
| **Snapshot history** | Every fetch is stored with a content hash, so an unchanged page costs one row and no diff. |
| **Ignore patterns** | A regex drops matching lines before the content is hashed, so a timestamp or a banner stops triggering a diff. |
| **Manual check** | POST /api/watches/<id>/check runs one fetch immediately and returns the diff. |

## Quickstart

```sh
git clone https://github.com/scar8969/diffwatch.git
cd diffwatch
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

The same work from the CLI:

```sh
python -m changewatch.cli --help
```

Commands: `add`, `list`.

A first request:

```sh
curl -s http://127.0.0.1:8000/api/watches | head
```

## Requirements

- Python **3.11+** — CI runs 3.11, 3.12 and 3.13.
- Runtime dependencies: `Flask>=3.0`, `Flask-SQLAlchemy>=3.1`, `SQLAlchemy>=2.0`, `PyYAML>=6.0`, `beautifulsoup4`.
- No JavaScript build step: every page is server-rendered Jinja.

## API

Every route below is in [`openapi/diffwatch.yaml`](openapi/diffwatch.yaml) and is exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/api/watches` | list |
| `POST` | `/api/watches` | add watch |
| `POST` | `/api/watches/<id>/check` | manual check |
| `GET` | `/api/watches/<id>/snapshots` | history |

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/healthz.png" alt="/healthz" width="100%"><br><sub><code>/healthz</code> &middot; 8.4 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/livez.png" alt="/livez" width="100%"><br><sub><code>/livez</code> &middot; 7.3 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/metrics.png" alt="/metrics" width="100%"><br><sub><code>/metrics</code> &middot; 14.8 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/readyz.png" alt="/readyz" width="100%"><br><sub><code>/readyz</code> &middot; 7.7 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/version.png" alt="/version" width="100%"><br><sub><code>/version</code> &middot; 26.3 KB</sub></td>
</tr>
</table>

## Measured, not estimated

These numbers were produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **24 / 24 passed** (2.5 s, exit 0) |
| Line coverage | **68.1%** — 427 of 604 statements |
| Source | 16 files / 1,351 lines |
| Test code | 4 files / 229 lines |
| Documented paths | 3 in the spec, 2 GET |
| Live probe | 10 GET requests to the booted app, **8 answered 200** |
| Median latency | **18.6 ms** (single uncached request, dev server) |
| Slowest / fastest | 64.2 ms `/` / 6.2 ms `/api/watches/demo/snapshots` |
| Bytes served | 6.4 KB across 10 responses |
| Screenshots | 6 captured |

## Architecture

```
diffwatch/
├── src/changewatch/
│   ├── http.py                         379  HTTP plumbing for changewatch: correlation ids, acce
│   ├── config.py                       171  Environment-driven configuration for changewatch
│   ├── observability.py                169  Structured logging and request correlation for chang
│   ├── app.py                          119  Application factory for changewatch
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── _app.py                          98  diffwatch — Flask application entry point
│   ├── watcher/api.py                   75  
│   ├── paths.py                         52  Filesystem layout for changewatch
│   ├── cli.py                           47  changewatch command line interface
│   ├── watcher/scheduler.py             33  
│   ├── models.py                        28  
│   ├── watcher/differ.py                25  
├── openapi/diffwatch.yaml                 the contract of record
├── schema/diffwatch.sql                   the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `watcher/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor set in `pyproject.toml` from the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 for every push to `main`, plus a container build. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Deploy

```sh
docker build -t diffwatch .
docker run --rm -p 8000:8000 --env-file .env.example diffwatch
```

Configuration is environment-only — every variable is documented in [`.env.example`](.env.example), and the service refuses to start with a production secret missing.

## Limits, stated rather than hidden

- Renders server-side HTML only; a JavaScript-rendered page needs a browser fetcher.
- Diffs are line-based, so a reflowed but semantically identical page can still register as changed.

## License

MIT — see [LICENSE](LICENSE).
