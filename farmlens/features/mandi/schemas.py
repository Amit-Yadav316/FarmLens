from __future__ import annotations

from pydantic import BaseModel


class PriceRequest(BaseModel):
    """Request model for mandi price lookup."""

    crop: str
    state: str
    market: str | None = None


class PriceRecord(BaseModel):
    """A single price record from the mandi."""

    market: str
    crop: str
    variety: str
    min_price: float
    max_price: float
    modal_price: float
    arrival_date: str


class PriceResponse(BaseModel):
    """Response model for mandi price lookup."""

    crop: str
    state: str
    records: list[PriceRecord]
    source: str = "Agmarknet"
