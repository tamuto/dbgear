from typing import Any
from dataclasses import asdict

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
    columns.extend([column.make_grid_column(**asdict(cell)) for cell in cells])

    # TODO データを変換

    return DataInfo(
        grid_columns=columns,
        grid_rows=[],
        allow_line_addition_and_removal=False
    )
