import json
from pathlib import Path

import httpx
from loguru import logger

from app.config.settings import OUTPUT_DIR, REQUEST_TIMEOUT
from app.middleware.retry import http_retry
from app.models.trademark import Trademark


def _filename_base(filing_number: str) -> str:
    """KH/49633/12  →  KH4963312"""
    return filing_number.replace("/", "")


def _html_path(filing_number: str) -> Path:
    return OUTPUT_DIR / f"{_filename_base(filing_number)}_1.html"


def _image_path(filing_number: str) -> Path:
    return OUTPUT_DIR / f"{_filename_base(filing_number)}_2.jpg"


def _build_detail_html(trademark: Trademark) -> str:
    """Generate a self-contained HTML page from trademark data."""
    image_tag = (
        f'<img src="{trademark.image_url}" alt="Trademark image" style="max-width:400px;">'
        if trademark.image_url
        else "<p><em>No image available.</em></p>"
    )
    raw_json = json.dumps(trademark.detail_data, indent=2, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{trademark.brand} — Cambodia IP Trademark Detail</title>
  <style>
    body {{ font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ color: #1a3c6e; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    td, th {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
    th {{ background: #f2f2f2; width: 200px; }}
    pre {{ background: #f8f8f8; padding: 1rem; overflow-x: auto; font-size: 0.85em; }}
  </style>
</head>
<body>
  <h1>{trademark.brand}</h1>
  <table>
    <tr><th>Filing Number</th><td>{trademark.filing_number}</td></tr>
    <tr><th>Owner</th><td>{trademark.owner}</td></tr>
  </table>
  <h2>Trademark Image</h2>
  {image_tag}
  <h2>Raw API Data</h2>
  <pre><code>{raw_json}</code></pre>
</body>
</html>"""


async def save_html(trademark: Trademark) -> Path:
    """Write the detail HTML page to disk and return its path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = _html_path(trademark.filing_number)
    html = _build_detail_html(trademark)
    path.write_text(html, encoding="utf-8")
    logger.info("Saved HTML → {}", path)
    return path


@http_retry
async def download_image(
    image_url: str,
    cookies: dict[str, str],
    client: httpx.AsyncClient,
) -> bytes | None:
    """Download the trademark image and return raw bytes, or None on failure."""
    logger.info("Downloading image: {}", image_url)
    try:
        response = await client.get(image_url, cookies=cookies, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            logger.warning("Image download returned HTTP {}", response.status_code)
            return None
        return response.content
    except httpx.TimeoutException:
        logger.warning("Timeout downloading image: {}", image_url)
        raise  # allow tenacity to retry


async def save_image(filing_number: str, data: bytes) -> Path:
    """Write image bytes to disk and return the path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = _image_path(filing_number)
    path.write_bytes(data)
    logger.info("Saved image → {}", path)
    return path
