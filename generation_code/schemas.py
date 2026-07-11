from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

PubType  = Literal["Conference", "Journal", "Workshop", "Preprint"]
WSField  = Literal["WS1", "WS2", "WS3", "WS4", "WS5", "O", "A"]


class Publication(BaseModel):
    model_config = ConfigDict(extra="allow")  # tolerate ad-hoc keys
    year: str
    title: str
    venue: str
    venue_acr: str
    type: PubType
    field: WSField
    authors: list[str]
    url: Optional[str] = None
    student: Optional[str] = None
    alumn: Optional[str] = None
    fig: Optional[str] = None
    note: Optional[str] = None
    pres: Optional[str] = None
    extras: Optional[dict[str, str]] = None
    onepager: Optional[bool] = None


class Stint(BaseModel):
    """One appointment (postdoc/phd/masters/intern/undergrad) a person held in the lab."""
    model_config = ConfigDict(extra="allow")
    program: Literal["postdoc", "phd", "other"]
    status: Literal["current", "alumni"]
    role: Optional[str] = None  # short CV/website tag for non-phd/postdoc stints, e.g. "MSR", "Intern"
    dept: Optional[str] = None
    start: Optional[int | str] = None
    year: Optional[int | str] = None  # graduation/departure year, alumni stints only
    capt: Optional[str] = None  # website-card caption (may contain HTML)
    topic: Optional[str] = None  # plain-text CV blurb
    thesis: Optional[str] = None  # formal thesis/dissertation title, phd alumni only
    pos: Optional[str] = None  # next position, alumni only
    co: Optional[str] = None
    co_url: Optional[str] = None


class PersonRecord(BaseModel):
    """A person and every stint (appointment) they've held in the lab."""
    model_config = ConfigDict(extra="allow")
    name: str
    url: Optional[str] = None
    pron: Optional[str] = None
    pic: Optional[str] = None
    native: Optional[str] = None
    x: Optional[str] = None
    ws: Optional[int] = None
    stints: list[Stint] = Field(default_factory=list)


class Affiliation(BaseModel):
    name: str
    affiliation: Optional[str] = None
    scholar_id: Optional[str] = None
