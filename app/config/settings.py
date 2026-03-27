from pathlib import Path

BASE_URL = "https://digitalip.cambodiaip.gov.kh"
SPA_URL = f"{BASE_URL}/en/trademark-search"
SEARCH_ENDPOINT = f"{BASE_URL}/api/v1/web/trademark-search"

OUTPUT_DIR = Path("output")
REQUEST_TIMEOUT = 30.0

FILING_NUMBERS = [
    "KH/49633/12",
    "KH/59286/14",
    "KH/83498/19",
]
