import urllib.parse

import httpx
from loguru import logger

from app.config.settings import BASE_URL, REQUEST_TIMEOUT, SEARCH_ENDPOINT
from app.middleware.retry import http_retry
from app.models.trademark import Trademark
from app.schemas.api_response import SearchResponse


def _build_payload(filing_number: str) -> dict:
    """Build the POST JSON payload for a filing-number search."""
    return {
        "data": {
            "page": "1",
            "perPage": "20",
            "search": {
                "key": "filing_number",
                "value": filing_number,
            },
            "advanceSearch": [],
            "dateOption": "",
            "isAdvanceSearch": "false",
            "filter": {
                "province": [],
                "country": [],
                "status": [],
                "applicationType": [],
                "markFeature": [],
                "classification": [],
                "date": [],
                "fillDate": [],
                "receptionDate": [],
                "regisDate": [],
            },
        }
    }


def _build_headers(cookies: dict[str, str]) -> dict[str, str]:
    """Build request headers including the URL-decoded XSRF token."""
    xsrf = urllib.parse.unquote(cookies.get("XSRF-TOKEN", ""))
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-XSRF-TOKEN": xsrf,
        "Referer": f"{BASE_URL}/en/trademark-search",
        "Origin": BASE_URL,
    }


@http_retry
async def search_trademark(
    filing_number: str,
    cookies: dict[str, str],
    client: httpx.AsyncClient,
) -> Trademark | None:
    """POST to the search API and return a Trademark, or None if not found."""
    logger.info("Searching for filing number: {}", filing_number)

    payload = _build_payload(filing_number)
    headers = _build_headers(cookies)

    response = await client.post(
        SEARCH_ENDPOINT,
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code != 200:
        logger.error(
            "Search failed for {} — HTTP {}", filing_number, response.status_code
        )
        return None

    try:
        parsed = SearchResponse.model_validate(response.json())
    except Exception as exc:
        logger.error("Failed to parse API response for {}: {}", filing_number, exc)
        return None

    records = (parsed.data.data if parsed.data else []) or []

    if not records:
        logger.warning("No results found for filing number: {}", filing_number)
        return None

    record = records[0]
    logger.info("Found trademark: {} — {}", record.brand, record.owner)

    image_url: str | None = None
    if record.logo and record.application_number:
        image_url = f"{BASE_URL}/trademark-detail-logo/{record.application_number}?type=ts_logo_detail_screen"

    return Trademark(
        filing_number=filing_number,
        brand=record.brand or "",
        owner=record.owner or "",
        image_url=image_url,
        detail_data=record.model_dump(by_alias=False),
    )
