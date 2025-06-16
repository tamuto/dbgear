from dbgear.core.models.base import BaseSchema
from dbgear.core.models.schema import Table, Field, Index, View, Schema
from dbgear.core.models.project import Binding
from dbgear.core.models.environ.data import Mapping
from dbgear.core.models.datagrid.data import DataModel
from dbgear.core.models.datagrid.data import DataInfo

# リクエスト用DTO


class NewMapping(BaseSchema):
    group: str
    base: str | None
    name: str
    instances: list = []
    description: str = ''
    deployment: bool


def convert_to_mapping(id: str, data: NewMapping) -> Mapping:
    return Mapping(
        id=id,
        **data.model_dump()
    )


class NewDataModel(BaseSchema):
    description: str
    layout: str
    settings: dict[str, object]
    sync_mode: str
    value: str | None = None
    caption: str | None = None
    segment: str | None = None
    x_axis: str | None = None
    y_axis: str | None = None
    cells: list[str] | None = None


def convert_to_data_model(
        data: NewDataModel,
        id: str = '',
        instance: str = '',
        table_name: str = '') -> DataModel:
    return DataModel(
        id=id,
        instance=instance,
        table_name=table_name,
        **data.model_dump()
    )


class ImportSQL(BaseSchema):
    host: str
    sql: str


# レスポンス用DTO


class Result(BaseSchema):
    status: str = 'OK'
    message: str | None = None
    data: object | list | None = None


class ProjectInfo(BaseSchema):
    project_name: str
    description: str
    bindings: dict[str, Binding]
    rules: dict[str, str]
    instances: list[str]
    api_key: str | None = None


class DataFilename(BaseSchema):
    id: str | None
    id_name: str | None
    instance: str
    table_name: str
    display_name: str | None
    description: str | None


def convert_to_data_filename(instance: str, tbl: Table, description: str | None = None, id: str | None = None, id_name: str | None = None):
    return DataFilename(
        id=id,
        id_name=id_name,
        instance=instance,
        table_name=tbl.table_name,
        display_name=tbl.display_name,
        description=description
    )


class Data(BaseSchema):
    model: DataModel
    info: DataInfo
    table: Table


class MappingTree(BaseSchema):
    name: str | None
    children: list[Mapping]


# スキーマ管理用DTO

class CreateSchemaRequest(BaseSchema):
    schema_name: str


class CreateTableRequest(BaseSchema):
    instance: str
    table_name: str
    display_name: str | None = None


class CreateFieldRequest(BaseSchema):
    column_name: str
    display_name: str | None = None
    column_type: str
    nullable: bool = True
    primary_key: int | None = None
    default_value: str | None = None
    foreign_key: str | None = None
    comment: str | None = None
    expression: str | None = None
    stored: bool | None = None
    auto_increment: bool | None = None
    charset: str | None = None
    collation: str | None = None


class UpdateFieldRequest(BaseSchema):
    column_name: str | None = None
    display_name: str | None = None
    column_type: str | None = None
    nullable: bool | None = None
    primary_key: int | None = None
    default_value: str | None = None
    foreign_key: str | None = None
    comment: str | None = None
    expression: str | None = None
    stored: bool | None = None
    auto_increment: bool | None = None
    charset: str | None = None
    collation: str | None = None


class CreateIndexRequest(BaseSchema):
    index_name: str | None = None
    columns: list[str]


class CreateViewRequest(BaseSchema):
    instance: str
    view_name: str
    display_name: str | None = None
    select_statement: str
    comment: str | None = None


class UpdateViewRequest(BaseSchema):
    view_name: str | None = None
    display_name: str | None = None
    select_statement: str | None = None
    comment: str | None = None


class ValidateTableRequest(BaseSchema):
    model_config = {"arbitrary_types_allowed": True}
    table: Table


class ValidateFieldRequest(BaseSchema):
    model_config = {"arbitrary_types_allowed": True}
    field: Field


class ValidateForeignKeyRequest(BaseSchema):
    model_config = {"arbitrary_types_allowed": True}
    field: Field
    schemas: dict[str, Schema]


def convert_to_field(data: CreateFieldRequest) -> Field:
    field_data = data.model_dump(exclude_unset=True)
    
    # Noneの値をデフォルト値に変換
    if 'display_name' not in field_data:
        field_data['display_name'] = field_data['column_name']
    if 'stored' not in field_data:
        field_data['stored'] = False
    if 'auto_increment' not in field_data:
        field_data['auto_increment'] = False
    if 'primary_key' not in field_data:
        field_data['primary_key'] = None
    if 'default_value' not in field_data:
        field_data['default_value'] = None
    if 'comment' not in field_data:
        field_data['comment'] = None
    
    return Field(**field_data)


def convert_to_index(data: CreateIndexRequest) -> Index:
    return Index(**data.model_dump())


def convert_to_view(data: CreateViewRequest) -> View:
    view_data = data.model_dump()
    
    # display_nameが設定されていない場合はview_nameを使用
    if not view_data.get('display_name'):
        view_data['display_name'] = view_data['view_name']
    
    return View(**view_data)


def convert_to_table(data: CreateTableRequest) -> Table:
    return Table(
        instance=data.instance,
        table_name=data.table_name,
        display_name=data.display_name,
        fields=[],
        indexes=[]
    )
