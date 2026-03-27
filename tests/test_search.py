"""
Integration test: performs a real trademark search against the API.
Requires a valid session (acquired via Playwright).
Run with: uv run pytest tests/test_search.py -v
"""

import pytest

import httpx

from app.services.search import search_trademark
from app.services.session import get_session_cookies


@pytest.fixture(scope="module")
async def cookies():
    return await get_session_cookies()


@pytest.mark.asyncio
async def test_search_known_filing_number(cookies):
    async with httpx.AsyncClient(cookies=cookies) as client:
        trademark = await search_trademark("KH/49633/12", cookies, client)

    assert trademark is not None
    assert trademark.filing_number == "KH/49633/12"
    assert trademark.brand  # non-empty
    assert trademark.owner  # non-empty


@pytest.mark.asyncio
async def test_search_nonexistent_returns_none(cookies):
    async with httpx.AsyncClient(cookies=cookies) as client:
        result = await search_trademark("KH/00000/00", cookies, client)

    assert result is None
