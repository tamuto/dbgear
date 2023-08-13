from typing import Any
from dataclasses import asdict

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import find_field

from .data import DataModel
from .data import GridColumn
from .data import DataInfo
from . import column
from .column import CellItem


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: Any) -> DataInfo:
    cells = column.make_cell_item(proj, map, dm, table)
    columns = _build_column(dm, table, cells)

    row_items = column.get_axis_items(proj, map, dm.settings, dm.y_axis, dm.instance)
    matrix = {k['value']: {dm.y_axis: k['value'], '_sort_key': k['caption']} for k in row_items}
    for d in data:
        y_data = d[dm.y_axis]
        if y_data not in matrix:
            continue
        for cell in cells:
            matrix[y_data][cell.column_name] = d[cell.column_name]
    rows = [{
        col.field: column.adjust_column_value(col, d)
        for col in columns} for d in sorted(matrix.values(), key=lambda x: x['_sort_key'])]

    return DataInfo(
        grid_columns=columns,
        grid_rows=rows,
        allow_line_addition_and_removal=False
    )


def _build_column(dm: DataModel, table: Table, cells: list[CellItem]) -> list[GridColumn]:
    columns = []
    field = find_field(table.fields, dm.y_axis)
    columns.append(column.make_grid_column(
        dm.y_axis,
        field.display_name,
        editable=False
    ))
    columns.extend([column.make_grid_column(**asdict(cell)) for cell in cells])
    return columns
