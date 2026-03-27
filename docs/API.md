Title: API Reference — Cambodia IP Trademark Portal
Description: Internal REST API endpoints discovered by inspecting SPA network traffic.

Base URL: https://digitalip.cambodiaip.gov.kh

---

Endpoint 1 — Search Trademarks

Method: POST
Path:   /api/v1/web/trademark-search
Auth:   Session cookies (XSRF-TOKEN, laravel_session) + X-XSRF-TOKEN header

Request Headers:
  Content-Type: application/json
  Accept: application/json
  X-XSRF-TOKEN: <URL-decoded value of XSRF-TOKEN cookie>
  Referer: https://digitalip.cambodiaip.gov.kh/en/trademark-search
  Origin: https://digitalip.cambodiaip.gov.kh

Request Body:
{
  "data": {
    "page": "1",
    "perPage": "20",
    "search": {
      "key": "filing_number",
      "value": "KH/49633/12"
    },
    "advanceSearch": [],
    "dateOption": "",
    "isAdvanceSearch": "false",
    "filter": {
      "province": [], "country": [], "status": [],
      "applicationType": [], "markFeature": [],
      "classification": [], "date": [],
      "fillDate": [], "receptionDate": [], "regisDate": []
    }
  }
}

Response (200 OK):
{
  "success": true,
  "message": "Success.",
  "data": {
    "data": [
      {
        "id": <int>,
        "filing_no": "KH/49633/12",
        "mark_name": "MINGFAI",
        "applicant_name": "Ming Fai Enterprise International Co., Ltd.",
        "image": "<relative or absolute image path>",
        "status": "<string>"
      }
    ],
    "meta": {
      "total": 1,
      "perPage": 20,
      "currentPage": 1
    }
  }
}

Notes:
- The response also sets fresh XSRF-TOKEN and laravel_session cookies (Max-Age 7200s).
- The SPA has a JSON serialization bug where search becomes "[object Object]<value>".
  Always construct the payload manually; do not rely on the SPA's request format.

---

Endpoint 2 — Trademark Image

Method: GET
URL:    <value of "image" field from search response>
Auth:   Same session cookies required; image requests without cookies return an error.

Response: Raw image bytes (JPEG).

---

Supporting Endpoints (not used by scraper):

GET /file/en.json                        — UI translation strings
GET /api/v1/web/get-setting              — Application settings (logo URLs, feature flags)
GET /file/68c398b44118b.json             — Country code → name mapping
