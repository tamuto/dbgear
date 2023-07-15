from .base import BaseSchema


class NewTemplate(BaseSchema):
    id: str
    name: str
    instances: list = []


class NewTemplateData(BaseSchema):
    instance: str
    table_name: str
    layout: str
    # TODO layoutのパラメータ追加予定
