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
    caption: Optional[str] = None  # alt text for `fig`; falls back to a generic title-based caption when unset
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
    # Byline to show when this person's published name differs from `name` (e.g. a
    # Chinese name published surname-first). `name` stays the key everything else
    # matches on -- publications.yaml, websites.yaml, the COA -- and only the
    # rendered author lists use `pubname`.
    pubname: Optional[str] = None
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


# The sections below used to live as literal \cventry calls inside
# CV_template.jinja2. They forbid unknown keys, so a mistyped key in the yaml is
# an error at generate time rather than a field that silently fails to print.

class Position(BaseModel):
    """One appointment, current or previous (yaml/positions.yaml)."""
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    when: int | str
    title: str
    where: Optional[str] = None
    url: Optional[str] = None
    # `with` is a Python keyword, so the field is with_ and the yaml key is the alias.
    with_: Optional[str] = Field(default=None, alias="with")
    detail: list[str] = Field(default_factory=list)


class Degree(BaseModel):
    """A degree earned (yaml/education.yaml)."""
    model_config = ConfigDict(extra="forbid")
    when: int | str
    degree: str
    where: Optional[str] = None
    honor: Optional[str] = None
    thesis: Optional[str] = None
    thesisurl: Optional[str] = None
    advisor: Optional[str] = None
    committee: Optional[str] = None
    reader: Optional[str] = None


class ReviewVenue(BaseModel):
    """A venue reviewed for, grouped by area (yaml/reviewing.yaml)."""
    model_config = ConfigDict(extra="forbid")
    acronym: str
    venue: str
    years: int | str


class OrgRole(BaseModel):
    """A workshop or conference organizing role (yaml/organization.yaml)."""
    model_config = ConfigDict(extra="forbid")
    kind: str
    what: str
    url: Optional[str] = None
    venue: Optional[str] = None


class Talk(BaseModel):
    """An invited talk or seminar visit (yaml/talks.yaml)."""
    model_config = ConfigDict(extra="forbid")
    title: Optional[str] = None
    url: Optional[str] = None
    venue: Optional[str] = None
    venueurl: Optional[str] = None
    host: Optional[str] = None


class CapstoneMember(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    pron: Optional[str] = None
    url: Optional[str] = None


class Capstone(BaseModel):
    """A masters capstone project and its team (yaml/capstones.yaml)."""
    model_config = ConfigDict(extra="forbid")
    program: str
    project: str
    when: int | str
    columns: int = 2
    url: Optional[str] = None
    co: Optional[str] = None
    courl: Optional[str] = None
    members: list[CapstoneMember] = Field(default_factory=list)


class ServiceItem(BaseModel):
    """Department/university service, grouped by year (yaml/service.yaml)."""
    model_config = ConfigDict(extra="forbid")
    what: str
    detail: Optional[str] = None
