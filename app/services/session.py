from loguru import logger
from playwright.async_api import async_playwright

from app.config.settings import SPA_URL


async def get_session_cookies() -> dict[str, str]:
    """Launch Chromium once, load the SPA, and return the session cookies."""
    logger.info("Launching browser to acquire session cookies...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(SPA_URL, wait_until="domcontentloaded", timeout=60_000)
        # Wait for the SPA to initialize and for the server to set cookies
        await page.wait_for_timeout(3_000)

        cookies = await context.cookies()
        await browser.close()

    cookie_map = {c["name"]: c["value"] for c in cookies}

    if "XSRF-TOKEN" not in cookie_map or "laravel_session" not in cookie_map:
        logger.warning("Expected cookies not found. Got: {}", list(cookie_map.keys()))
    else:
        logger.info("Session cookies acquired successfully.")

    return cookie_map
