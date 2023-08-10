from typing import Any
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


class GridColumn(BaseSchema):
    field: str
    type: str
    header_name: str
    width: int
    editable: bool
    items: list = []
    hide: bool = False


class DataInfo(BaseSchema):
    grid_columns: list[GridColumn] = []
    grid_rows: list[dict[str, Any]] = []
