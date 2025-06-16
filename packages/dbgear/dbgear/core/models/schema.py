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
    
    def add_field(self, field: Field) -> None:
        if self.field_exists(field.column_name):
            raise ValueError(f"Field '{field.column_name}' already exists in table '{self.table_name}'")
        self.fields.append(field)
    
    def remove_field(self, field_name: str) -> None:
        field = self.get_field(field_name)
        self.fields.remove(field)
    
    def update_field(self, field_name: str, field: Field) -> None:
        for i, existing_field in enumerate(self.fields):
            if existing_field.column_name == field_name:
                self.fields[i] = field
                return
        raise KeyError(f"Field '{field_name}' not found in table '{self.table_name}'")
    
    def get_field(self, field_name: str) -> Field:
        for field in self.fields:
            if field.column_name == field_name:
                return field
        raise KeyError(f"Field '{field_name}' not found in table '{self.table_name}'")
    
    def field_exists(self, field_name: str) -> bool:
        return any(field.column_name == field_name for field in self.fields)
    
    def add_index(self, index: Index) -> None:
        if index.index_name and self.get_index(index.index_name) is not None:
            raise ValueError(f"Index '{index.index_name}' already exists in table '{self.table_name}'")
        self.indexes.append(index)
    
    def remove_index(self, index_name: str) -> None:
        index = self.get_index(index_name)
        if index is None:
            raise KeyError(f"Index '{index_name}' not found in table '{self.table_name}'")
        self.indexes.remove(index)
    
    def get_index(self, index_name: str) -> Index | None:
        for index in self.indexes:
            if index.index_name == index_name:
                return index
        return None


class Schema:

    def __init__(self, name):
        self.name = name
        self.tables = {}

    def __repr__(self) -> str:
        return f'{self.tables}'

    def add_table(self, table: Table) -> None:
        self.tables[table.table_name] = table

    def remove_table(self, table_name: str) -> None:
        if table_name not in self.tables:
            raise KeyError(f"Table '{table_name}' not found in schema '{self.name}'")
        del self.tables[table_name]

    def update_table(self, table_name: str, table: Table) -> None:
        if table_name not in self.tables:
            raise KeyError(f"Table '{table_name}' not found in schema '{self.name}'")
        self.tables[table_name] = table

    def table_exists(self, table_name: str) -> bool:
        return table_name in self.tables

    def get_table(self, name: str) -> Table:
        return self.tables[name]

    def get_tables(self) -> dict[str, Table]:
        return self.tables


def find_field(fields: list[Field], name: str):
    field = next(filter(lambda x: x.column_name == name, fields), None)
    if field is None:
        raise RuntimeError(f'Could not find field. ({name})')
    return field
