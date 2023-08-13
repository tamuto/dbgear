from typing import Any
from dataclasses import asdict

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from .. import const

from .data import DataModel
from .data import DataInfo
from . import column


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: Any) -> DataInfo:
    columns = []
    columns.append(column.make_grid_column(
        dm.y_axis,
        '',
        editable=False
    ))

    items = _get_x_axis_items(proj, map, dm)
    cells = column.make_cell_item(proj, map, dm, table)
    columns.extend([
        column.make_grid_column(
            **asdict(cell, dict_factory=column.exclude_names),
            column_name=f"{item['value']}_{cell.column_name}",
            display_name=f"{item['caption']}({cell.display_name})"
        ) for cell in cells for item in items
    ])

    # TODO データをマトリックスへ変換

    return DataInfo(
        grid_columns=columns,
        grid_rows=[],
        allow_line_addition_and_removal=False
    )


def _get_x_axis_items(proj: Project, map: Mapping, dm: DataModel) -> list[object]:
    items = None
    setting = dm.settings[dm.x_axis]
    if setting['type'] == const.BIND_TYPE_FOREIGN_KEY:
        items = column.load_for_select_items(proj.folder, map, dm.instance, setting['value'])
    elif setting['type'] == const.BIND_TYPE_EMBEDDED_DATA:
        items = setting['values']
    elif setting['type'] in proj.bindings:
        bind = proj.bindings[setting['type']]
        if bind.type == const.BIND_TYPE_SELECTABLE:
            items = bind.items
    if items is None:
        raise RuntimeError('No Data for X axis.')
    return items
