from typing import Any
from dataclasses import asdict

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import find_field
from ..fileio import load_data
from .. import const

from .column import CellItem
from .data import DataModel
from .data import GridColumn
from .data import DataInfo
from . import column
from . import layout_table


def build(proj: Project, map: Mapping, dm: DataModel, table: Table) -> DataInfo:
    data = load_data(proj.folder, map.id, table.instance, table.table_name, None)
    field = find_field(table.fields, dm.y_axis)
    row_items = column.get_axis_items(proj, map, dm.settings, dm.y_axis, dm.instance)
    cells = column.make_cell_item(proj, map, dm, table)
    columns = _build_column(dm, field.display_name, row_items, cells)

    matrix = {k.value: {dm.y_axis: k.value, '_sort_key': k.caption} for k in row_items}
    for d in data:
        y_data = d[dm.y_axis]
        if y_data not in matrix:
            continue
        for cell in cells:
            matrix[y_data][cell.column_name] = d[cell.column_name]
    rows = [column.make_one_row(columns, d) for d in sorted(matrix.values(), key=lambda x: x['_sort_key'])]

    return DataInfo(
        segments=None,
        current=None,
        grid_columns=columns,
        grid_rows=rows,
        allow_line_addition_and_removal=False
    )


def _build_column(dm: DataModel, display_name: str, row_items: list[object], cells: list[CellItem]) -> list[GridColumn]:
    width = const.DEFAULT_WIDTH
    if 'width' in dm.settings[dm.y_axis]:
        width = dm.settings[dm.y_axis]['width']
    columns = []
    columns.append(column.make_grid_column(
        dm.y_axis,
        display_name,
        type=const.FIELD_TYPE_SELECTABLE,
        width=width,
        editable=False,
        items=row_items
    ))
    columns.extend([column.make_grid_column(**asdict(cell)) for cell in cells])
    return columns


def parse(proj: Project, map: Mapping, dm: DataModel, table: Table, rows: object) -> list[dict[str, Any]]:
    expdata = [
        {
            dm.y_axis: row[dm.y_axis],
            **{cell: row[cell] for cell in dm.cells}
        }
        for row in rows]
    return layout_table.parse(proj, map, dm, table, None, expdata)
