import asyncio
import httpx

COOKIES = {
    "XSRF-TOKEN": "TU_TOKEN_AQUI",
    "laravel_session": "TU_SESSION_AQUI",
}

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-XSRF-TOKEN": "TU_TOKEN_AQUI",  # Laravel requiere esto también
    "Referer": "https://digitalip.cambodiaip.gov.kh/en/trademark-search",
}

PAYLOAD = {
    "data": {
        "page": "1",
        "perPage": "20",
        "search": {"key": "filing_number", "value": "KH/49633/12"},
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


async def test():
    async with httpx.AsyncClient(cookies=COOKIES) as client:
        r = await client.post(
            "https://digitalip.cambodiaip.gov.kh/api/v1/web/trademark-search",
            json=PAYLOAD,
            headers=HEADERS,
        )
        print(r.status_code)
        print(r.json())


asyncio.run(test())
