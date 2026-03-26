# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraper technical test for **UNUMBIO SpA**. The goal is to scrape trademark information from [Cambodia's IP portal](https://digitalip.cambodiaip.gov.kh/en/trademark-search), which is a SPA (Single Page Application) backed by an internal REST API.

## Tech Stack

- **Python 3.11** (via `venv/`)
- **Playwright** (async) — browser automation for session cookie acquisition
- **aiohttp / httpx / curl_cffi** — direct HTTP requests (choose one; minimize browser usage)
- **tenacity** — retry logic for transient failures
- **Full async/await** throughout

## Key Architecture Decisions

The scraper separates two concerns:
1. **Browser phase** (Playwright): Launch browser once to obtain session cookies from the SPA.
2. **HTTP phase** (aiohttp/httpx/curl_cffi): Use those cookies for all subsequent requests (detail page HTML, image downloads) without spawning more browser instances.

The internal REST API endpoints must be discovered by inspecting network calls in the browser (DevTools / Playwright's `on("request")`). Direct HTTP calls to the API avoid full page loads and are far faster.

## Commands

### Setup
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Run the scraper
```bash
python app/main.py
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
