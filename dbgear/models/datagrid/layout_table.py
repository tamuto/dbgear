from typing import Any

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import Field
from .. import const

from .data import DataModel
from .data import GridColumn
from .data import DataInfo
from . import column


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: Any) -> DataInfo:
    # フィールドを設定に従って展開する。ForeignKeyなども設定に含まれるものとする。
    columns = build_columns(proj, map, dm, table)
    rows = [column.build_one_row(columns, d) for d in data]

    return DataInfo(
        grid_columns=columns,
        grid_rows=rows,
        allow_line_addition_and_removal=True
    )


def build_one_row(proj: Project, map: Mapping, dm: DataModel, table: Table) -> dict[str, Any]:
    columns = build_columns(proj, map, dm, table)
    return column.build_one_row(columns, {})


def build_columns(proj: Project, map: Mapping, dm: DataModel, table: Table) -> list[GridColumn]:
    columns = []
    for field in table.fields:
        if field.column_name in dm.settings:
            grid_column = _make_grid_column_from_setting(proj, map, dm, field)
        else:
            grid_column = column.make_grid_column(
                field.column_name,
                field.display_name)

        columns.append(grid_column)
    return columns


def _make_grid_column_from_setting(proj: Project, map: Mapping, dm: DataModel, field: Field):
    setting = dm.settings[field.column_name]
    if setting['type'] == const.BIND_TYPE_FOREIGN_KEY:
        # 選択肢は外部データを参照する以外は選択型と同じ
        splt = setting['value'].split('.')
        items = column.load_for_select_items(proj.folder, map, splt[0], splt[1])
        if items is None:
            # データが見つからなければ空の配列とする
            items = []
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            items=items)

    bind = proj.bindings[setting['type']]
    if bind.type == const.BIND_TYPE_FIXED:
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            editable=False,
            hide=True,
            fixed_value=bind.value)
    if bind.type == const.BIND_TYPE_CALL:
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            editable=False,
            call_value=bind.value)
    if bind.type == const.BIND_TYPE_SELECTABLE:
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            items=bind.items)
    raise RuntimeError('Unknown Data Type')


def parse(proj: Project, map: Mapping, dm: DataModel, table: Table, rows: object) -> list[dict[str, Any]]:
    # idカラムを除いて返却する。
    columns = build_columns(proj, map, dm, table)
    data = [column.build_one_row(columns, d, False) for d in rows]
    return data
