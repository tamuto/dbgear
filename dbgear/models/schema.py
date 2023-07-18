from typing import Union
from .base import BaseSchema


class Schema:

    def __init__(self, name):
        self.name = name
        self.tables = {}

    def __repr__(self) -> str:
        return f'{self.tables}'

    def add_table(self, table):
        self.tables[table.table_name] = table

    def get_table(self, name):
        return self.tables[name]

    def info(self):
        return sorted(
            [
                {'table_name': t.table_name, 'display_name': t.display_name}
                for t in self.tables.values()
            ],
            key=lambda x: x['table_name'])


class Field(BaseSchema):
    column_name: str
    display_name: str
    column_type: str
    nullable: bool
    primary_key: Union[int, None]
    default_value: Union[str, None]
    foreign_key: Union[str, None]
    comment: Union[str, None]


class Index(BaseSchema):
    index_name: Union[str, None]
    columns: list[str]


class Table(BaseSchema):
    table_name: str
    display_name: str
    fields: list[Field] = []
    indexes: list[Index] = []
    # FIXME 参照元をデータとして持たせるか？
