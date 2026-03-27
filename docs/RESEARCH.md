# Research & Investigation Notes

## 1. Site Investigation

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

## 2. Architecture Decision — Hybrid Strategy

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

## 3. Technical Decisions

| Decision | Reason |
|----------|--------|
| httpx over aiohttp | Simpler API, same async performance, built-in JSON support |
| pydantic for API response | Catches schema drift early; self-documenting |
| asyncio.gather for trademarks | All three run concurrently — no sequential waiting |
| tenacity for retries | Declarative, configurable backoff without boilerplate |
| loguru for logging | Structured, colored output with minimal setup |
| XSRF-TOKEN URL-decoded | The cookie value is URL-encoded; Laravel expects the decoded form in the header |

## 4. Detail HTML Strategy

The site is a SPA with no accessible static detail URLs. Rather than using
Playwright to render each detail page (slow, resource-heavy), the scraper
generates a self-contained HTML page from the API JSON response fields.
This is faster and produces an equivalent artifact.
