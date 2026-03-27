# UNUMBIO — Cambodia IP Trademark Scraper

Async Python scraper that downloads trademark detail pages and images from
[Cambodia's IP portal](https://digitalip.cambodiaip.gov.kh/en/trademark-search).

---

## Setup

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
make install
# equivalent to: uv sync && uv run playwright install chromium
```

## Run

```bash
make run
# equivalent to: uv run python main.py
```

Output files are saved to `output/`:

```
output/
  KH4963312_1.html    # Detail page for KH/49633/12
  KH4963312_2.jpg     # Image for KH/49633/12
  KH5928614_1.html
  KH5928614_2.jpg
  KH8349819_1.html
  KH8349819_2.jpg
```

## Test / Lint

```bash
make test    # uv run pytest tests/
make lint    # uv run ruff check .
make format  # uv run ruff format .
```

---

## Thought Process

### 1. Site Investigation

The target is a SPA (Vue/React) that communicates with a Laravel backend via a
REST API. I opened DevTools → Network and observed:

- On page load, the server sets two cookies: `XSRF-TOKEN` and `laravel_session`.
- All search requests are `POST /api/v1/web/trademark-search` with a JSON body.
- Images are served from a URL found in the search JSON response, and the request
  **requires the session cookies** — a plain `requests.get()` without cookies returns
  an error.

I also discovered a bug in the SPA's JavaScript: when building the search payload,
it serializes the `search` object incorrectly, producing
`"search": "[object Object]49633"` instead of the proper nested object. This means
the SPA's own requests are broken for filing-number searches. The fix is to
construct the correct JSON payload directly in Python.

### 2. Architecture Decision — Hybrid Strategy

The key insight is that Playwright is only needed **once**, to let the browser
execute the SPA's JavaScript so the server sets the session cookies. After that,
all subsequent communication is plain HTTP with those cookies.

```
Playwright (once at startup)
  └── Load SPA → capture XSRF-TOKEN + laravel_session cookies
          ↓
httpx AsyncClient (concurrent, handles all trademarks)
  ├── POST /api/v1/web/trademark-search  →  get JSON data
  ├── Build HTML detail page from JSON
  ├── GET <image_url>  (with cookies)    →  download image bytes
  └── Save: KH<num>_1.html + KH<num>_2.jpg
```

This avoids spawning a browser instance per trademark (which would be 3× slower
and far more resource-intensive).

### 3. Technical Decisions

| Decision | Reason |
|----------|--------|
| httpx over aiohttp | Simpler API, same async performance, built-in JSON support |
| pydantic for API response | Catches schema drift early; self-documenting |
| asyncio.gather for trademarks | All three run concurrently — no sequential waiting |
| tenacity for retries | Declarative, configurable backoff without boilerplate |
| loguru for logging | Structured, colored output with minimal setup |
| XSRF-TOKEN URL-decoded | The cookie value is URL-encoded; Laravel expects the decoded form in the header |

### 4. Detail HTML Strategy

The site is a SPA with no accessible static detail URLs. Rather than using
Playwright to render each detail page (slow, resource-heavy), the scraper
generates a self-contained HTML page from the API JSON response fields.
This is faster and produces an equivalent artifact.

---

## Actual Time Spent

- Site investigation and API discovery: ~45 minutes
- Architecture planning: ~15 minutes
- Implementation: ~1.5 hours
- Testing and debugging: ~30 minutes
- Documentation: ~30 minutes

Total: approximately 3.5 hours
