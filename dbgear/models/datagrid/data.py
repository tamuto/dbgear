from typing import Any
from pydantic import Field
from ..base import BaseSchema


class DataModel(BaseSchema):
    id: str
    instance: str
    table_name: str
    description: str = ''
    layout: str
    settings: dict[str, object]
    sync_mode: str
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
    hide: bool = False
    items: list | None = None
    fixed_value: str | None = None
    call_value: str | None = None


class DataInfo(BaseSchema):
    grid_columns: list[GridColumn]
    grid_rows: list[dict[str, Any]]
    allow_line_addition_and_removal: bool
