import asyncio
from playwright.async_api import async_playwright


async def get_session_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(
            "https://digitalip.cambodiaip.gov.kh/en/trademark-search",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        await page.wait_for_timeout(3000)  # espera que la SPA inicialice y setee cookies
        cookies = await context.cookies()
        await browser.close()
        return {c["name"]: c["value"] for c in cookies}


if __name__ == "__main__":
    cookies = asyncio.run(get_session_cookies())
    print(cookies)
