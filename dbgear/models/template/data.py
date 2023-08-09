from pydantic import Field

from ..base import BaseSchema


class Mapping(BaseSchema):
    id: str = Field(exclude=True)
    name: str
    instances: list[str] = []
    description: str = ''
