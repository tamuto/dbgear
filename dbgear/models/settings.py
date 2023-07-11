from .base import BaseSchema


class Settings(BaseSchema):
    id: str
    name: str
    instances: list = []
