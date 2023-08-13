from typing import Any
from pydantic import Field
from ..base import BaseSchema


class DataModel(BaseSchema):
    id: str = Field(exclude=True)
    instance: str = Field(exclude=True)
    table_name: str = Field(exclude=True)
    description: str = ''
    layout: str
    settings: dict[str, object]
    value: str | None = None
    caption: str | None = None
    x_axis: str | None = None
    y_axis: str | None = None
    cells: list[str] | None = None


class GridColumn(BaseSchema):
    field: str
    type: str
    header_name: str
    width: int
    editable: bool
    items: list | None = None
    hide: bool = False


class DataInfo(BaseSchema):
    grid_columns: list[GridColumn] = []
    grid_rows: list[dict[str, Any]] = []
    allow_line_addition_and_removal: bool
