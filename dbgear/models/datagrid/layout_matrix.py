from typing import Any
from dataclasses import asdict

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table

from .data import DataModel
from .data import GridColumn
from .data import DataInfo
from . import column
from . import layout_table
from .column import CellItem


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: Any) -> DataInfo:
    items = column.get_axis_items(proj, map, dm.settings, dm.x_axis, dm.instance)
    cells = column.make_cell_item(proj, map, dm, table)
    columns = _build_columns(dm, items, cells)

    row_items = column.get_axis_items(proj, map, dm.settings, dm.y_axis, dm.instance)
    matrix = {k['value']: {dm.y_axis: k['value'], '_sort_key': k['caption']} for k in row_items}
    for d in data:
        y_data = d[dm.y_axis]
        if y_data not in matrix:
            continue
        for cell in cells:
            matrix[y_data][f"{d[dm.x_axis]}_{cell.column_name}"] = d[cell.column_name]
    rows = [column.build_one_row(columns, d) for d in sorted(matrix.values(), key=lambda x: x['_sort_key'])]

    return DataInfo(
        grid_columns=columns,
        grid_rows=rows,
        allow_line_addition_and_removal=False
    )


def _build_columns(dm: DataModel, items: list[object], cells: list[CellItem]) -> list[GridColumn]:
    columns = []
    columns.append(column.make_grid_column(
        dm.y_axis,
        '',
        editable=False
    ))
    columns.extend([
        column.make_grid_column(
            **asdict(cell, dict_factory=column.exclude_names),
            column_name=f"{item['value']}_{cell.column_name}",
            display_name=f"{item['caption']}({cell.display_name})"
        ) for cell in cells for item in items
    ])
    return columns


def parse(proj: Project, map: Mapping, dm: DataModel, table: Table, rows: object) -> list[dict[str, Any]]:
    items = column.get_axis_items(proj, map, dm.settings, dm.x_axis, dm.instance)
    expdata = [{
        dm.y_axis: row[dm.y_axis],
        dm.x_axis: col['value'],
        cell: row[f"{col['value']}_{cell}"]
    } for cell in dm.cells for col in items for row in rows]

    return layout_table.parse(proj, map, dm, table, expdata)
