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
        grid_column = _make_grid_column_from_setting(proj, map, dm, field)
        columns.append(grid_column)
    return columns


def _make_grid_column_from_setting(proj: Project, map: Mapping, dm: DataModel, field: Field):
    if field.column_name not in dm.settings:
        return column.make_grid_column(
            field.column_name,
            field.display_name)

    setting = dm.settings[field.column_name]
    if setting['type'] == const.BIND_TYPE_BLANK:
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH)

    if setting['type'] == const.BIND_TYPE_REFS:
        # 選択肢は外部データを参照する以外は選択型と同じ
        id = setting['id']
        ins = setting['instance']
        tbl = setting['table']
        items = column.load_for_select_items(proj.folder, id, ins, tbl)
        if items is None:
            # データが見つからなければ空の配列とする
            items = []
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            type=const.FIELD_TYPE_SELECTABLE,
            width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH,
            items=items)

    bind = proj.bindings[setting['type']]
    if bind.type == const.BIND_TYPE_FIXED:
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH,
            editable=False,
            hide=True,
            fixed_value=bind.value)
    if bind.type == const.BIND_TYPE_CALL:
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH,
            editable=False,
            call_value=bind.value)
    if bind.type == const.BIND_TYPE_SELECTABLE:
        return column.make_grid_column(
            field.column_name,
            field.display_name,
            width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH,
            type=const.FIELD_TYPE_SELECTABLE,
            items=bind.items)
    raise RuntimeError('Unknown Data Type')


def parse(proj: Project, map: Mapping, dm: DataModel, table: Table, rows: object) -> list[dict[str, Any]]:
    # idカラムを除いて返却する。
    columns = build_columns(proj, map, dm, table)
    data = [column.build_one_row(columns, d, False) for d in rows]
    return data
