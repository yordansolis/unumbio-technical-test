from dataclasses import dataclass, field


@dataclass
class Trademark:
    filing_number: str
    brand: str
    owner: str
    image_url: str | None = field(default=None)
    detail_data: dict = field(default_factory=dict)
