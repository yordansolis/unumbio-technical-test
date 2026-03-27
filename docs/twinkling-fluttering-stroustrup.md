# Plan: UNUMBIO Web Scraping Technical Test

## Context
Build a production-grade async Python scraper for Cambodia's IP trademark portal. The project skeleton (empty directories) already exists. Two prototype scripts (`test.py`, `test_cookies.py`) prove the API works. The task is to wire everything together into a clean, structured application.

---

## Critical Files to Create/Modify

| File | Action |
|------|--------|
| `app/config/settings.py` | Create — BASE_URL, timeouts, filing numbers, output dir |
| `app/models/trademark.py` | Create — Trademark dataclass |
| `app/schemas/api_response.py` | Create — Pydantic model for API JSON response |
| `app/middleware/logger.py` | Create — loguru setup |
| `app/middleware/retry.py` | Create — tenacity decorators |
| `app/services/session.py` | Create — Playwright cookie extractor |
| `app/services/search.py` | Create — httpx POST search_trademark() |
| `app/services/downloader.py` | Create — download_image(), save_html() |
| `main.py` | Rewrite — async entry point |
| `pyproject.toml` | Update — add pydantic, ruff; remove unused requests |
| `Makefile` | Fill in — install/run/test/lint/format targets |
| `tests/test_session.py` | Move from test_cookies.py |
| `tests/test_search.py` | Move from test.py |
| `tests/test_downloader.py` | Create stub |
| `output/.gitkeep` | Create |
| `docs/API.md` | Create — endpoints, payloads, response schema |
| `docs/ARCHITECTURE.md` | Create — hybrid strategy diagram |
| `README.md` | Rewrite — setup, thought process, time spent |

---

## Implementation Steps

### 1. pyproject.toml
- Add `pydantic>=2.0` (for `api_response.py`)
- Add `ruff` as dev dependency
- Remove `requests` (unused; everything uses httpx)
- Remove `pytest-playwright` (add plain `pytest` + `pytest-asyncio`)

### 2. app/config/settings.py
```python
BASE_URL = "https://digitalip.cambodiaip.gov.kh"
SEARCH_ENDPOINT = f"{BASE_URL}/api/v1/web/trademark-search"
SPA_URL = f"{BASE_URL}/en/trademark-search"
OUTPUT_DIR = Path("output")
REQUEST_TIMEOUT = 30.0
FILING_NUMBERS = ["KH/49633/12", "KH/59286/14", "KH/83498/19"]
```

### 3. app/models/trademark.py
Dataclass with fields: `filing_number`, `brand`, `owner`, `image_url`, `html_content`

### 4. app/schemas/api_response.py
Pydantic models matching the API JSON response structure (discovered via Investigacion.md research).

### 5. app/middleware/logger.py
Configure loguru with format: `{time} | {level} | {message}`

### 6. app/middleware/retry.py
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
```
Apply to `search_trademark()` and `download_image()`.

### 7. app/services/session.py
Migrate from `test_cookies.py`:
- `async def get_session_cookies() -> dict[str, str]`
- Uses headless Chromium, navigates to SPA_URL, waits for cookies, returns dict
- Capture both `XSRF-TOKEN` and `laravel_session`

### 8. app/services/search.py
Migrate API call from `test.py`:
- `async def search_trademark(filing_number: str, cookies: dict, client: httpx.AsyncClient) -> Trademark | None`
- POST to SEARCH_ENDPOINT with correct payload (key: filing_number, value: <number>)
- Set headers: `Content-Type`, `Accept`, `X-XSRF-TOKEN`, `Referer`
- Parse response → return Trademark or None if not found
- Wrapped with tenacity retry decorator

### 9. app/services/downloader.py
- `async def download_image(image_url: str, cookies: dict, client: httpx.AsyncClient) -> bytes | None`
  - GET image URL with session cookies; return raw bytes or None
  - Wrapped with tenacity retry decorator
- `async def save_html(filing_number: str, html: str) -> Path`
  - Write `output/KH<num>_1.html`
- `async def save_image(filing_number: str, data: bytes) -> Path`
  - Write `output/KH<num>_2.jpg`
- Filename helper: `KH/49633/12` → `KH4963312`

### 10. main.py (rewrite)
```python
async def process_trademark(filing_number, cookies, client):
    trademark = await search_trademark(filing_number, cookies, client)
    if not trademark: return
    await save_html(filing_number, trademark.html_content)
    image = await download_image(trademark.image_url, cookies, client)
    if image:
        await save_image(filing_number, image)

async def main():
    cookies = await get_session_cookies()   # Playwright — runs once
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[
            process_trademark(fn, cookies, client)
            for fn in FILING_NUMBERS
        ])
```

### 11. tests/
- Move `test_cookies.py` → `tests/test_session.py` (fix imports)
- Move `test.py` → `tests/test_search.py` (fix imports, use env-var cookies)
- Create `tests/test_downloader.py` (stub with filename-generation tests)

### 12. Makefile
```makefile
install:
	uv sync && uv run playwright install chromium
run:
	uv run python main.py
test:
	uv run pytest tests/
lint:
	uv run ruff check .
format:
	uv run ruff format .
```

---

## Detail Page HTML — Strategy
The spec requires saving a "detail HTML page" for each trademark. The site is a SPA so there is no static detail URL. **Approach:** construct the detail HTML ourselves from the API JSON response fields (title, owner, filing number, image tag, etc.) and save it as a self-contained HTML file. This satisfies the requirement while avoiding unnecessary browser usage.

---

## Error Handling Matrix

| Scenario | Behavior |
|----------|----------|
| API returns 0 results | Log warning → skip filing number |
| httpx timeout / network error | tenacity retries 3× → log error → skip |
| Image URL missing in response | Log info → save HTML only |
| HTTP 4xx/5xx | Log status code → skip |

---

## Verification
1. `make install` — installs deps + Chromium
2. `make run` — executes scraper; expect 6 files in `output/`
3. Verify `output/KH4963312_1.html`, `KH4963312_2.jpg`, `KH5928614_1.html`, `KH5928614_2.jpg`, `KH8349819_1.html`, `KH8349819_2.jpg`
4. `make test` — all tests pass
5. `make lint` — no ruff errors
