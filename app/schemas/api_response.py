from pydantic import BaseModel, Field


class TrademarkRecord(BaseModel):
    """A single trademark record from the search API response."""

    id: int | None = None
    filing_number: str | None = Field(default=None, alias="filing_no")
    brand: str | None = Field(default=None, alias="mark_name")
    owner: str | None = Field(default=None, alias="applicant_name")
    image_path: str | None = Field(default=None, alias="image")
    status: str | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class SearchMeta(BaseModel):
    total: int = 0
    per_page: int = Field(default=20, alias="perPage")
    current_page: int = Field(default=1, alias="currentPage")

    model_config = {"populate_by_name": True, "extra": "allow"}


class SearchData(BaseModel):
    data: list[TrademarkRecord] = []
    meta: SearchMeta | None = None

    model_config = {"extra": "allow"}


class SearchResponse(BaseModel):
    success: bool = False
    message: str = ""
    data: SearchData | None = None

    model_config = {"extra": "allow"}
