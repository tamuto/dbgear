from typing import Any

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import Field
from ..fileio import load_data
from .. import const

from .data import DataModel
from .data import ListItem
from .data import GridColumn
from .data import DataInfo
from . import column


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, segment: str | None) -> DataInfo:
    # フィールドを設定に従って展開する。ForeignKeyなども設定に含まれるものとする。
    columns, seg_info = build_columns(proj, map, dm, table)
    if seg_info is None:
        data = load_data(proj.folder, map.id, table.instance, table.table_name, None)
        rows = [column.make_one_row(columns, d) for d in data]
        return DataInfo(
            segments=None,
            current=None,
            grid_columns=columns,
            grid_rows=rows,
            allow_line_addition_and_removal=True
        )

    if segment is None:
        segment = seg_info[1][0].value

    data = load_data(proj.folder, map.id, table.instance, table.table_name, segment)
    rows = [column.make_one_row(columns, d) for d in data]

    return DataInfo(
        segments=seg_info[1],
        current=segment,
        grid_columns=columns,
        grid_rows=rows,
        allow_line_addition_and_removal=True
    )


def build_one_row(proj: Project, map: Mapping, dm: DataModel, table: Table) -> dict[str, Any]:
    # ここでは画面表示用のデータ生成のため、セグメントは不要。
    columns, _ = build_columns(proj, map, dm, table)
    return column.make_one_row(columns, {})


def build_columns(proj: Project, map: Mapping, dm: DataModel, table: Table) -> tuple[list[GridColumn], tuple[str, list[ListItem]] | None]:
    columns = []
    items = None
    for field in table.fields:
        if field.column_name == dm.segment:
            # セグメントは表示しないせずに、セグメントリストを作成する。
            setting = dm.settings[field.column_name]
            # 仮にrefs以外が設定されていた場合にはidやinstanceなどがないので、エラーとなる。
            assert setting['type'] == const.BIND_TYPE_REFS
            id = setting['id']
            ins = setting['instance']
            tbl = setting['table']
            items = column.load_for_select_items(proj.folder, id, ins, tbl)
            if items is None:
                raise RuntimeError('Segment items not found.')
            continue
        grid_column = _make_grid_column_from_setting(proj, map, dm, field)
        columns.append(grid_column)
    if items is None:
        return columns, None
    return columns, (dm.segment, items)


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
    raise RuntimeError('Unknown Data Type')


def parse(proj: Project, map: Mapping, dm: DataModel, table: Table, segment: str | None, rows: object) -> list[dict[str, Any]]:
    # idカラムを除いて返却する。
    columns, seg_info = build_columns(proj, map, dm, table)
    if seg_info is None:
        data = [column.make_one_row(columns, d, need_id=False) for d in rows]
        return data
    # seg_infoがある場合には、セグメントカラムを作成する。
    assert segment is not None
    data = [
        column.make_one_row(
            columns,
            d,
            need_id=False,
            segment=(True, seg_info[0], segment)
        ) for d in rows
    ]
    return data
