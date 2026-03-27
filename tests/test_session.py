"""
Integration test: acquires real session cookies via Playwright.
Requires a network connection and an installed Chromium browser.
Run with: uv run pytest tests/test_session.py -v
"""

import pytest

from app.services.session import get_session_cookies


@pytest.mark.asyncio
async def test_get_session_cookies_returns_expected_keys():
    cookies = await get_session_cookies()
    assert "XSRF-TOKEN" in cookies, "XSRF-TOKEN cookie not found"
    assert "laravel_session" in cookies, "laravel_session cookie not found"
    assert len(cookies["XSRF-TOKEN"]) > 10
    assert len(cookies["laravel_session"]) > 10
