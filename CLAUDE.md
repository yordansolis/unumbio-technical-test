# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraper technical test for **UNUMBIO SpA**. The goal is to scrape trademark information from [Cambodia's IP portal](https://digitalip.cambodiaip.gov.kh/en/trademark-search), which is a SPA (Single Page Application) backed by an internal REST API.

## Tech Stack

- **Python 3.11+** managed via `uv`
- **Playwright** (async) — browser automation for session cookie acquisition
- **httpx** — async HTTP client for direct API and image requests
- **tenacity** — retry logic for transient failures
- **loguru** — structured logging
- **pydantic v2** — data validation and schema models
- **ruff** — linting and formatting
- **pytest + pytest-asyncio** — test suite

## Project Structure

```
unumbio-technical-test/
├── main.py                  # Entry point
├── app/
│   ├── config/
│   │   └── settings.py      # Centralised settings (URLs, timeouts, filing numbers)
│   ├── middleware/
│   │   ├── logger.py        # Loguru setup
│   │   └── retry.py         # Tenacity retry decorators
│   ├── models/
│   │   └── trademark.py     # Domain model (TrademarkRecord)
│   ├── schemas/
│   │   └── api_response.py  # Pydantic schemas for API responses
│   └── services/
│       ├── session.py       # Browser phase — Playwright cookie acquisition
│       ├── search.py        # Search service — API call to find trademark by filing number
│       └── downloader.py    # Download service — detail HTML + trademark image
├── tests/
│   ├── test_session.py
│   ├── test_search.py
│   └── test_downloader.py
├── output/                  # Scraped files (gitignored except .gitkeep)
├── pyproject.toml
├── Makefile
└── uv.lock
```

## Key Architecture Decisions

The scraper separates two concerns:
1. **Browser phase** (`session.py`): Launch Playwright once to obtain session cookies from the SPA.
2. **HTTP phase** (`search.py`, `downloader.py`): Use those cookies with `httpx` for all subsequent requests — API search, detail page HTML, image downloads — without spawning more browser instances.

Direct HTTP calls to the internal REST API avoid full page loads and are far faster.

## Commands

### Setup
```bash
uv sync
uv run playwright install chromium
```

### Run the scraper
```bash
uv run python main.py
# or
make run
```

### Test
```bash
uv run pytest tests/
# or
make test
```

### Lint / Format
```bash
make lint
make format
```

### Clean output
```bash
make clean
```

### Output
Files are saved to `output/` with naming convention `KH<number-without-slashes>_1.html` (detail HTML) and `KH<number-without-slashes>_2.jpg` (trademark image).

## Filing Numbers to Scrape

| Filing Number | Trademark | Owner |
|---------------|-----------|-------|
| KH/49633/12 | MINGFAI | Ming Fai Enterprise International Co., Ltd. |
| KH/59286/14 | Eesatto | DIAMOND POINT Sdn Bhd |
| KH/83498/19 | FORCE | TIFORCE INTERNATIONAL CO., LTD. |

## Error Handling Requirements

- **Not found**: log and continue to next number
- **Timeout**: retry before failing
- **No image**: log and continue without error

## Git Workflow

Title: Git Workflow - Commit Messages (Conventional Commits)
Description: Standardized structure for writing commit messages that facilitates reading, automation, and maintenance of the project history. Use the format <type>(<scope>): <description>, where type defines the type of change made.

Types: feat, fix, refactor, test, docs, chore, perf
Scopes: backend

Examples:
feat(backend): add workflow completion
fix(backend): handle expired session cookies
