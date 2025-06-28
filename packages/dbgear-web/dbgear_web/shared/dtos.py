from dbgear.models.base import BaseSchema
from dbgear.models.schema import Schema
from dbgear.models.table import Table
from dbgear.models.column import Column
from dbgear.models.index import Index
from dbgear.models.view import View

# レスポンス用DTO


class Result(BaseSchema):
    status: str = 'OK'
    message: str | None = None
    data: object | list | None = None


class ProjectInfo(BaseSchema):
    project_name: str
    description: str
    bindings: dict[str, object] = {}
    rules: dict[str, str] = {}
    instances: list[str] = []
    api_key: str | None = None


class DataFilename(BaseSchema):
    id: str | None
    id_name: str | None
    instance: str
    table_name: str
    display_name: str | None
    description: str | None


# スキーマ管理用DTO

class CreateSchemaRequest(BaseSchema):
    schema_name: str


class CreateTableRequest(BaseSchema):
    instance: str
    table_name: str
    display_name: str | None = None


class CreateColumnRequest(BaseSchema):
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


class UpdateColumnRequest(BaseSchema):
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


class ValidateColumnRequest(BaseSchema):
    model_config = {"arbitrary_types_allowed": True}
    column: Column


class ValidateForeignKeyRequest(BaseSchema):
    model_config = {"arbitrary_types_allowed": True}
    column: Column
    schemas: dict[str, Schema]


def convert_to_column(data: CreateColumnRequest) -> Column:
    column_data = data.model_dump(exclude_unset=True)

    # Noneの値をデフォルト値に変換
    if 'display_name' not in column_data:
        column_data['display_name'] = column_data['column_name']
    if 'stored' not in column_data:
        column_data['stored'] = False
    if 'auto_increment' not in column_data:
        column_data['auto_increment'] = False
    if 'primary_key' not in column_data:
        column_data['primary_key'] = None
    if 'default_value' not in column_data:
        column_data['default_value'] = None
    if 'comment' not in column_data:
        column_data['comment'] = None

    return Column(**column_data)


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
        columns=[],
        indexes=[]
    )


# Relations API DTOs

class CreateRelationRequest(BaseSchema):
    relation_name: str | None = None
    target_schema: str
    target_table: str
    bind_columns: list[dict[str, str]]  # [{"source": "col1", "target": "col2"}]
    on_delete: str | None = None  # CASCADE, SET NULL, RESTRICT
    on_update: str | None = None  # CASCADE, SET NULL, RESTRICT
    logical_only: bool = False


class UpdateRelationRequest(BaseSchema):
    relation_name: str | None = None
    target_schema: str | None = None
    target_table: str | None = None
    bind_columns: list[dict[str, str]] | None = None
    on_delete: str | None = None
    on_update: str | None = None
    logical_only: bool | None = None


# Notes API DTOs

class CreateNoteRequest(BaseSchema):
    title: str
    content: str
    checked: bool = False


class UpdateNoteRequest(BaseSchema):
    title: str | None = None
    content: str | None = None
    checked: bool | None = None


# Triggers API DTOs

class CreateTriggerRequest(BaseSchema):
    trigger_name: str
    table_name: str
    timing: str  # BEFORE, AFTER
    event: str   # INSERT, UPDATE, DELETE
    statement: str
    comment: str | None = None


class UpdateTriggerRequest(BaseSchema):
    trigger_name: str | None = None
    table_name: str | None = None
    timing: str | None = None
    event: str | None = None
    statement: str | None = None
    comment: str | None = None


# Column Types API DTOs

class CreateColumnTypeRequest(BaseSchema):
    type_name: str
    base_type: str
    length: int | None = None
    precision: int | None = None
    scale: int | None = None
    items: list[str] | None = None  # For ENUM/SET
    description: str | None = None


class UpdateColumnTypeRequest(BaseSchema):
    type_name: str | None = None
    base_type: str | None = None
    length: int | None = None
    precision: int | None = None
    scale: int | None = None
    items: list[str] | None = None
    description: str | None = None


# Tenant API DTOs

class CreateTenantRequest(BaseSchema):
    tenant_id: str
    name: str
    description: str | None = None
    config: dict[str, object] | None = None


class UpdateTenantRequest(BaseSchema):
    name: str | None = None
    description: str | None = None
    config: dict[str, object] | None = None


class CreateDatabaseRequest(BaseSchema):
    database_name: str
    host: str
    port: int | None = None
    username: str | None = None
    password: str | None = None
    connection_params: dict[str, object] | None = None


# Environment Management DTOs

class CreateEnvironmentRequest(BaseSchema):
    name: str
    description: str | None = None
    options: dict[str, object] | None = None


class UpdateEnvironmentRequest(BaseSchema):
    name: str | None = None
    description: str | None = None
    options: dict[str, object] | None = None


# Mapping Management DTOs

class CreateMappingRequest(BaseSchema):
    name: str
    group: str | None = None
    base: str | None = None
    instances: list[str] | None = None
    description: str | None = None
    deployment: bool = False


class UpdateMappingRequest(BaseSchema):
    name: str | None = None
    group: str | None = None
    base: str | None = None
    instances: list[str] | None = None
    description: str | None = None
    deployment: bool | None = None


# Data Model Management DTOs

class CreateDataModelRequest(BaseSchema):
    description: str
    layout: str
    settings: dict[str, object] | None = None
    sync_mode: str
    value: str | None = None
    caption: str | None = None
    segment: str | None = None
    x_axis: str | None = None
    y_axis: str | None = None
    cells: list[str] | None = None


class UpdateDataModelRequest(BaseSchema):
    description: str | None = None
    layout: str | None = None
    settings: dict[str, object] | None = None
    sync_mode: str | None = None
    value: str | None = None
    caption: str | None = None
    segment: str | None = None
    x_axis: str | None = None
    y_axis: str | None = None
    cells: list[str] | None = None


class CreateDataSourceRequest(BaseSchema):
    segment: str | None = None
    data: list[dict[str, object]]


class UpdateDataSourceRequest(BaseSchema):
    data: list[dict[str, object]]


# Database Operations DTOs

class DeployRequest(BaseSchema):
    environment: str
    mapping: str
    schemas: list[str] | None = None
    tables: list[str] | None = None
    drop_existing: bool = False
    apply_data: bool = False


class DeployPreviewRequest(BaseSchema):
    environment: str
    mapping: str
    schemas: list[str] | None = None
    tables: list[str] | None = None


class DeployJobResponse(BaseSchema):
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float | None = None
    message: str | None = None
    executed_operations: list[str] | None = None


class CreateDatabaseOperationRequest(BaseSchema):
    environment: str
    database_name: str
    force: bool = False


class ApplyDataRequest(BaseSchema):
    environment: str
    mapping: str
    schemas: list[str] | None = None
    tables: list[str] | None = None
    truncate_existing: bool = False
