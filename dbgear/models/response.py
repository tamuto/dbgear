from typing import Dict
from .base import BaseSchema


class Result(BaseSchema):
    status: str
    message: str | None = None


class ProjectInfo(BaseSchema):
    project_name: str
    templates: list
    environs: list
    instances: list
    column_settings: list
    rules: Dict[str, str]
