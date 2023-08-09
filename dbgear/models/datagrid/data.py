from pydantic import Field
from ..base import BaseSchema


class DataModel(BaseSchema):
    id: str = Field(exclude=True)
    instance: str = Field(exclude=True)
    table_name: str = Field(exclude=True)
    description: str = ''
    layout: str
    settings: dict[str, str]
    # TODO layoutの情報のパラメータ追加する


class DataInfo(BaseSchema):
    grid_columns: list = []
    grid_rows: list = []


class GridColumns(BaseSchema):
    field: str
    type: str
    header_name: str
    width: int
    editable: bool
    items: list = []
    hide: bool = False
