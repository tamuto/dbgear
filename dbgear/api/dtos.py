from ..models.base import BaseSchema
from ..models.schema import Table
from ..models.environ.data import Mapping
from ..models.datagrid.data import DataModel
from ..models.datagrid.data import DataInfo

# リクエスト用DTO


class NewMapping(BaseSchema):
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
    settings: dict[str, str]
    value: str
    caption: str
    x_axis: str | None = None
    y_axis: str | None = None


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

# レスポンス用DTO


class Result(BaseSchema):
    status: str = 'OK'
    message: str | None = None
    data: object | list | None = None


class ProjectInfo(BaseSchema):
    project_name: str
    templates: list
    environs: list
    instances: list
    column_settings: list
    rules: dict[str, str]


class DataFilename(BaseSchema):
    instance: str
    table_name: str
    display_name: str


def convert_to_data_filename(instance: str, tbl: Table):
    return DataFilename(
        instance=instance,
        table_name=tbl.table_name,
        display_name=tbl.display_name
    )


class Data(BaseSchema):
    model: DataModel
    info: DataInfo
    table: Table
