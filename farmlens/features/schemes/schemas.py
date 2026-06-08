from __future__ import annotations

from pydantic import BaseModel


class SchemeRequest(BaseModel):
    """Request model for government scheme lookup."""

    query: str
    language: str = "hi"


class Scheme(BaseModel):
    """A single government scheme entry."""

    name: str
    name_hi: str
    description: str
    description_hi: str
    eligibility: str
    benefit: str
    url: str


class SchemeResponse(BaseModel):
    """Response model for government scheme lookup."""

    schemes: list[Scheme]
    query: str
