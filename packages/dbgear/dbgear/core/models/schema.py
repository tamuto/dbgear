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
    
    # Column expression support
    expression: str | None = None  # Generated column expression
    stored: bool = False          # STORED/VIRTUAL distinction
    auto_increment: bool = False  # AUTO_INCREMENT attribute
    charset: str | None = None    # Character set for string columns
    collation: str | None = None  # Collation for string columns


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


class ViewColumn(BaseSchema):
    """View column definition (auto-generated from SQL parsing)"""
    column_name: str
    display_name: str
    column_type: str
    nullable: bool
    source_table: str | None = None  # 参照元テーブル
    source_column: str | None = None  # 参照元カラム
    is_computed: bool = False  # 計算列かどうか
    comment: str | None = None


class View(BaseSchema):
    """Database view definition"""
    instance: str
    view_name: str
    display_name: str
    select_statement: str
    comment: str | None = None
    
    # 以下は将来のSQL解析で自動生成される予定
    _parsed_columns: list[ViewColumn] = []  # SQL解析結果をキャッシュ
    _dependencies: list[str] = []  # 参照テーブル/ビューを自動検出
    _is_parsed: bool = False  # 解析済みフラグ
    
    def get_columns(self, schema_registry=None) -> list[ViewColumn]:
        """Get view columns (future: parse SQL automatically)"""
        if not self._is_parsed and schema_registry:
            self._parse_sql(schema_registry)
        return self._parsed_columns
    
    def get_dependencies(self, schema_registry=None) -> list[str]:
        """Get dependencies (future: parse SQL automatically)"""
        if not self._is_parsed and schema_registry:
            self._parse_sql(schema_registry)
        return self._dependencies
    
    def _parse_sql(self, schema_registry):
        """Future: Parse SQL and extract columns/dependencies"""
        # TODO: SQL解析実装
        # - FROM句からテーブル/ビュー依存関係を抽出
        # - SELECT句からカラム定義を推定
        # - 参照先テーブルの型情報から自動でViewColumnを生成
        pass


class Schema:

    def __init__(self, name):
        self.name = name
        self.tables = {}
        self.views = {}

    def __repr__(self) -> str:
        return f'Tables: {self.tables}, Views: {self.views}'

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

    def add_view(self, view: View) -> None:
        self.views[view.view_name] = view

    def remove_view(self, view_name: str) -> None:
        if view_name not in self.views:
            raise KeyError(f"View '{view_name}' not found in schema '{self.name}'")
        del self.views[view_name]

    def update_view(self, view_name: str, view: View) -> None:
        if view_name not in self.views:
            raise KeyError(f"View '{view_name}' not found in schema '{self.name}'")
        self.views[view_name] = view

    def view_exists(self, view_name: str) -> bool:
        return view_name in self.views

    def get_view(self, view_name: str) -> View:
        return self.views[view_name]

    def get_views(self) -> dict[str, View]:
        return self.views


def find_field(fields: list[Field], name: str):
    field = next(filter(lambda x: x.column_name == name, fields), None)
    if field is None:
        raise RuntimeError(f'Could not find field. ({name})')
    return field
