# Web Scraping – Technical Test
**UNUMBIO SpA** | Confidential | 2026-03-26

---

## Objective

Develop a Python scraper that downloads trademark information from Cambodia's intellectual property portal.

**Site URL:** https://digitalip.cambodiaip.gov.kh/en/trademark-search

---

## Site Description

The Cambodia IP portal is a **SPA (Single Page Application)** web application that allows searching for trademarks by different criteria. The one of interest is the **Filing Number**.

### Relevant Characteristics

- It is a SPA that dynamically loads content via JavaScript and calls to an **internal REST API**.
- Trademark images require **session cookies** to be downloaded. Without those cookies, the download fails.
- It has no captcha or login, but the cookie-based protection means a simple `requests.get()` **does not work** for everything.

### The Main Challenge

The candidate must investigate the network calls to discover how the web actually works and build the search correctly using the **fewest possible resources**.

---

## Numbers to Download

The scraper must successfully download **at least** the following 3 numbers:

| # | Filing Number | Trademark | Owner |
|---|---------------|-----------|-------|
| 1 | KH/49633/12 | MINGFAI | Ming Fai Enterprise International Co., Ltd. |
| 2 | KH/59286/14 | Eesatto | DIAMOND POINT Sdn Bhd |
| 3 | KH/83498/19 | FORCE | TIFORCE INTERNATIONAL CO., LTD. |

> All three numbers have an associated image.

---

## Technical Requirements

### Mandatory Stack

| Component | Technology |
|-----------|------------|
| Browser automation | Playwright (async) |
| HTTP requests | `aiohttp`, `httpx` or `curl_cffi` (choose one) |
| Language | Python 3.10+ |
| Async | The entire scraper must be asynchronous (`async/await`) |

### What the Scraper Must Do

For each number in the list, the scraper must retrieve:

- The **trademark detail page** (save as `.html`).
- The **trademark image** (save as `.jpg`).

> The most **performant** solution is valued. The candidate must decide which operations truly require a browser and which can be handled with pure HTTP. Sound judgment in minimizing browser usage where unnecessary is expected.

### Output File Naming

Files are saved in an `output/` folder. Each filename is built from the number **without `/`** followed by `_` and the page/file number:

```
output/
├── KH4963312_1.html   # Detail page for KH/49633/12
├── KH4963312_2.jpg    # Image for KH/49633/12
├── KH5928614_1.html
├── KH5928614_2.jpg
├── KH8349819_1.html
└── KH8349819_2.jpg
```

---

## Error Handling

The scraper must handle at least the following cases:

- **Number not found:** When the search returns no results, log the error and continue with the next one.
- **Load timeout:** If the page does not load within a reasonable time, retry before failing.
- **Image unavailable:** If the trademark has no image, log it and continue without error.

### Retries

The scraper is expected to implement retries for operations that may fail due to network issues or slow site loading. The `tenacity` library may be used, or retries can be implemented manually.

---

## Evaluation Criteria

| Criterion | Description |
|-----------|-------------|
| **Site investigation** | Ability to analyze network calls and understand how the API works behind the UI. |
| **Performance** | Knowing what requires a browser vs. what can be done with direct HTTP. Minimizing resource usage. |
| **Cookies & session** | Understanding the site's protection and correctly handling cookies between the browser and HTTP client. |
| **Asynchronous code** | Correct use of `async/await`. |
| **Error handling & retries** | The scraper must not crash on transient failures. |
| **Code structure & clarity** | Readable, well-organized code with informative logs. |

---

## Deliverable

Create a **public GitHub repository** with the scraper code. The repository must include:

- `requirements.txt` or `pyproject.toml` with dependencies. Any package manager may be used (`pip`, `uv`, `poetry`).
- The scraper source code.
- The downloaded files in the `output/` folder as evidence of successful execution.
- `README.md` that includes:
  - Instructions for installing dependencies and running the scraper.
  - **Thought process:** document how the problem was approached, what was investigated, what was discovered about the site, and why each technical decision was made.
  - **Actual time spent:** how long it took to complete the test.

Submit the **repository URL** upon completion.