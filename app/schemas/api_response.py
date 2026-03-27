from pydantic import BaseModel, Field


class TrademarkRecord(BaseModel):
    """A single trademark record from the search API response."""

    id: str | None = None
    brand: str | None = Field(default=None, alias="title")
    owner: str | None = None
    logo: bool = False
    application_number: str | None = None
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
