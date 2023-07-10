from dataclasses import dataclass
from dataclasses import field


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


@dataclass
class Field:
    column_name: str = None
    display_name: str = None
    column_type: str = None
    nullable: str = None
    primary_key: int = None
    default_value: str = None
    foreign_key: str = None
    comment: str = None


@dataclass
class Index:
    index_name: str = None
    columns: list[str] = field(default_factory=list)


@dataclass
class Table:
    table_name: str = None
    display_name: str = None
    fields: list[Field] = field(default_factory=list)
    indexes: list[Index] = field(default_factory=list)
    # FIXME 参照元をデータとして持たせるか？
