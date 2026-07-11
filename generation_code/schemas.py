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


class Person(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    url: Optional[str] = None
    pron: Optional[str] = None
    pic: Optional[str] = None
    dept: Optional[str] = None
    start: Optional[int | str] = None
    capt: Optional[str] = None
    ws: Optional[int] = None
    co: Optional[str] = None
    co_url: Optional[str] = None


class Affiliation(BaseModel):
    name: str
    affiliation: Optional[str] = None
    scholar_id: Optional[str] = None
