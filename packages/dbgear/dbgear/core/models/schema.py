import pydantic

from .base import BaseSchema


class Column(BaseSchema):
    column_name: str
    display_name: str
    column_type: str
    nullable: bool
    primary_key: int | None = None
    default_value: str | None = None
    foreign_key: str | None = None
    comment: str | None = None

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
    instance: str = pydantic.Field(exclude=True)
    table_name: str = pydantic.Field(exclude=True)
    display_name: str
    columns: list[Column] = []
    indexes: list[Index] = []
    # FIXME 参照元をデータとして持たせるか？

    def add_column(self, column: Column) -> None:
        if self.column_exists(column.column_name):
            raise ValueError(f"Column '{column.column_name}' already exists in table '{self.table_name}'")
        self.columns.append(column)

    def remove_column(self, column_name: str) -> None:
        column = self.get_column(column_name)
        self.columns.remove(column)

    def update_column(self, column_name: str, column: Column) -> None:
        for i, existing_column in enumerate(self.columns):
            if existing_column.column_name == column_name:
                self.columns[i] = column
                return
        raise KeyError(f"Column '{column_name}' not found in table '{self.table_name}'")

    def get_column(self, column_name: str) -> Column:
        for column in self.columns:
            if column.column_name == column_name:
                return column
        raise KeyError(f"Column '{column_name}' not found in table '{self.table_name}'")

    def column_exists(self, column_name: str) -> bool:
        return any(column.column_name == column_name for column in self.columns)

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


class Schema(BaseSchema):
    """Database schema containing tables and views"""
    name: str = pydantic.Field(exclude=True)
    tables: dict[str, Table] = {}
    views: dict[str, View] = {}

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


class SchemaManager(BaseSchema):
    """Manages multiple schemas in a database project"""
    schemas: dict[str, Schema] = {}

    def add_schema(self, schema: Schema) -> None:
        if schema.name in self.schemas:
            raise ValueError(f"Schema '{schema.name}' already exists")
        self.schemas[schema.name] = schema

    def remove_schema(self, name: str) -> None:
        if name not in self.schemas:
            raise KeyError(f"Schema '{name}' not found")
        del self.schemas[name]

    def get_schema(self, name: str) -> Schema:
        return self.schemas[name]

    def get_schemas(self) -> dict[str, Schema]:
        return self.schemas

    def schema_exists(self, name: str) -> bool:
        return name in self.schemas


# def find_field(fields: list[Field], name: str):
#     field = next(filter(lambda x: x.column_name == name, fields), None)
#     if field is None:
#         raise RuntimeError(f'Could not find field. ({name})')
#     return field
