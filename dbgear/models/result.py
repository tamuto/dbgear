from typing import Union
from .base import BaseSchema


class Result(BaseSchema):
    status: str
    message: Union[str, None] = None


class ProjectInfo(BaseSchema):
    project_name: str
    templates: list
    environs: list
    instances: list
