from __future__ import annotations
from pydantic import Field

from ..base import BaseSchema


class Mapping(BaseSchema):
    group: str
    base: str | None
    instances: list[str] = []
    description: str = ''
    deployment: bool

    # FIXME https://github.com/pydantic/pydantic/issues/5992
    parent: Mapping | None = Field(default=None)


class Instance(BaseSchema):
    display_name: str
    name: str
    base_schema: str


class Environ(BaseSchema):
    name: str
    deployment: bool
    instances: list[Instance] = []
