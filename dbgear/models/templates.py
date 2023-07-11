from .base import BaseSchema


class NewTemplate(BaseSchema):
    id: str
    name: str
    instances: list = []
