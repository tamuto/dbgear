from typing import Any

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import find_field

from .data import DataModel
from .data import DataInfo
from . import column


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: Any) -> DataInfo:
    columns = []
    field = find_field(table.fields, dm.y_axis)
    columns.append(column.make_grid_column(
        dm.y_axis,
        field.display_name,
        editable=False
    ))

    cells = column.make_cell_item(proj, map, dm, table)
    for cell in cells:
        columns.append(
            column.make_grid_column(
                cell.column_name,
                cell.display_name,
                type=cell.type,
                editable=cell.editable,
                items=cell.items
            )
        )

    # TODO データを変換

    return DataInfo(
        grid_columns=columns,
        grid_rows=[],
        allow_line_addition_and_removal=False
    )
