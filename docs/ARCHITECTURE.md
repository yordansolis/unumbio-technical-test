Title: Architecture — Hybrid Browser + HTTP Strategy
Description: The scraper separates browser automation from data retrieval into two distinct phases to maximize performance and minimize resource usage.

Phase 1 — Browser (Playwright, runs once at startup):
  Launch headless Chromium and navigate to the SPA.
  The server sets XSRF-TOKEN and laravel_session cookies on page load.
  Extract both cookies and close the browser immediately.

Phase 2 — HTTP (httpx AsyncClient, handles all remaining work):
  Use the acquired cookies for all subsequent requests.
  POST /api/v1/web/trademark-search with the filing number payload.
  GET the image URL from the response, passing the same session cookies.
  Save the detail HTML page and JPG image to output/.

Diagram:

  Playwright (once)
    └── Load SPA → capture XSRF-TOKEN + laravel_session
            ↓
  httpx AsyncClient (all trademarks, concurrent via asyncio.gather)
    ├── POST /api/v1/web/trademark-search  →  JSON with trademark data
    ├── Build detail HTML from JSON fields
    ├── GET <image_url> with cookies       →  raw image bytes
    └── Save: output/KH<num>_1.html + output/KH<num>_2.jpg

Key Decisions:

1. Playwright used only once — avoids the overhead of full page loads for each trademark.
2. httpx over requests — native async support, no thread-pool hacks required.
3. asyncio.gather — all three trademarks are processed concurrently.
4. The SPA has a JSON serialization bug (search becomes "[object Object]49633").
   We bypass the SPA entirely and construct the correct payload directly.
5. XSRF-TOKEN must be URL-decoded before passing as the X-XSRF-TOKEN header.
6. Detail HTML is generated from the API JSON response (the site is a SPA with
   no accessible static detail URLs).
