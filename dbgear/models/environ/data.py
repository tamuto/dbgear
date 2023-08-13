from pydantic import Field

from ..base import BaseSchema


class Mapping(BaseSchema):
    id: str = Field(exclude=True)
    base: str | None
    name: str
    instances: list[str] = []
    description: str = ''
    deployment: bool
