import asyncio

import httpx
from loguru import logger

from app.config.settings import FILING_NUMBERS
from app.middleware.logger import setup_logger
from app.services.downloader import download_image, save_html, save_image
from app.services.search import search_trademark
from app.services.session import get_session_cookies


async def process_trademark(
    filing_number: str,
    cookies: dict[str, str],
    client: httpx.AsyncClient,
) -> bool:
    """Search, download and save a single trademark. Returns True on success."""
    try:
        trademark = await search_trademark(filing_number, cookies, client)
    except Exception as exc:
        logger.error("Search failed for {} after retries: {}", filing_number, exc)
        return False

    if trademark is None:
        return False

    await save_html(trademark)

    if not trademark.image_url:
        logger.info("No image URL for {}; skipping image download.", filing_number)
        return True

    try:
        image_data = await download_image(trademark.image_url, cookies, client)
    except Exception as exc:
        logger.error("Image download failed for {} after retries: {}", filing_number, exc)
        return True  # HTML was saved; treat as partial success

    if image_data:
        await save_image(filing_number, image_data)
    else:
        logger.info("Image unavailable for {}.", filing_number)

    return True


async def main() -> None:
    setup_logger()
    logger.info("=== UNUMBIO Trademark Scraper ===")
    logger.info("Filing numbers to process: {}", FILING_NUMBERS)

    cookies = await get_session_cookies()

    async with httpx.AsyncClient(cookies=cookies) as client:
        results = await asyncio.gather(
            *[
                process_trademark(fn, cookies, client)
                for fn in FILING_NUMBERS
            ],
            return_exceptions=False,
        )

    successes = sum(1 for r in results if r)
    failures = len(results) - successes
    logger.info("=== Done: {} succeeded, {} failed ===", successes, failures)


if __name__ == "__main__":
    asyncio.run(main())
