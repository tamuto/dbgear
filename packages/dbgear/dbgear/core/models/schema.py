from .base import BaseSchema


class Field(BaseSchema):
    column_name: str
    display_name: str
    column_type: str
    nullable: bool
    primary_key: int | None
    default_value: str | None
    foreign_key: str | None
    comment: str | None


class Index(BaseSchema):
    index_name: str | None
    columns: list[str]


class Table(BaseSchema):
    instance: str
    table_name: str
    display_name: str
    fields: list[Field] = []
    indexes: list[Index] = []
    # FIXME 参照元をデータとして持たせるか？


class Schema:

    def __init__(self, name):
        self.name = name
        self.tables = {}

    def __repr__(self) -> str:
        return f'{self.tables}'

    def add_table(self, table: Table) -> None:
        self.tables[table.table_name] = table

    def get_table(self, name: str) -> Table:
        return self.tables[name]

    def get_tables(self) -> dict[str, Table]:
        return self.tables


def find_field(fields: list[Field], name: str):
    field = next(filter(lambda x: x.column_name == name, fields), None)
    if field is None:
        raise RuntimeError(f'Could not find field. ({name})')
    return field
