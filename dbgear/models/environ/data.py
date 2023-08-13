from __future__ import annotations
from pydantic import Field

from ..base import BaseSchema


class Mapping(BaseSchema):
    id: str = Field(exclude=True)
    base: str | None
    name: str
    instances: list[str] = []
    description: str = ''
    deployment: bool

    # FIXME https://github.com/pydantic/pydantic/issues/5992
    parent: Mapping | None = Field(exclude=True, default=None)
