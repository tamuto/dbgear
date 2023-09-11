from typing import Any
from dataclasses import dataclass
from uuid import uuid4

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import find_field
from ..fileio import load_all_data
from ..fileio import load_model
from ..fileio import get_data_model_name
from .. import const

from .data import DataModel
from .data import ListItem
from .data import GridColumn


def make_grid_column(
        column_name: str,
        display_name: str,
        *,
        type: str = const.FIELD_TYPE_STRING,
        width: int = const.DEFAULT_WIDTH,
        editable: bool = True,
        hide: bool = False,
        items: list[ListItem] | None = None,
        fixed_value: str | None = None,
        call_value: str | None = None):
    '''
    GridColumnを生成する。
    '''
    return GridColumn(
        field=column_name,
        type=type,
        header_name=display_name,
        width=width,
        editable=editable,
        hide=hide,
        items=items,
        fixed_value=fixed_value,
        call_value=call_value,
    )


def load_for_select_items(folder: str, id: str, ins: str, ref: str) -> list[ListItem]:
    '''
    マスタデータをロードして、選択肢用データを生成する。
    '''
    items = load_all_data(folder, id, ins, ref)
    if items is not None:
        # データが見つかった場合には、DataModelをロードし、
        # caption, valueのデータを生成する
        dm: DataModel = load_model(
            get_data_model_name(folder, id, ins, ref),
            DataModel,
            id=id,
            instance=ins,
            table_name=ref
        )
        if dm.caption is not None and dm.value is not None:
            items = [ListItem(
                caption=item[dm.caption],
                value=item[dm.value]
            ) for item in items]
        else:
            raise RuntimeError('Invalid Data Model for Master Data.')
    return items


@dataclass
class CellItem:
    column_name: str
    display_name: str
    type: str = const.FIELD_TYPE_STRING
    width: int = const.DEFAULT_WIDTH
    editable: bool = True
    items: list[ListItem] | None = None
    fixed_value: str | None = None
    call_value: str | None = None


def make_cell_item(proj: Project, map: Mapping, dm: DataModel, table: Table) -> list[CellItem]:
    '''
    セルの設定を生成する。
    '''
    result = []
    for cell in dm.cells:
        field = find_field(table.fields, cell)
        if cell in dm.settings:
            setting = dm.settings[cell]
            if setting['type'] == const.BIND_TYPE_BLANK:
                result.append(CellItem(
                    column_name=field.column_name,
                    display_name=field.display_name,
                    width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH
                ))
            elif setting['type'] == const.BIND_TYPE_REFS:
                id = setting['id']
                ins = setting['instance']
                tbl = setting['table']
                items = load_for_select_items(proj.folder, id, ins, tbl)

                result.append(CellItem(
                    column_name=field.column_name,
                    display_name=field.display_name,
                    type=const.FIELD_TYPE_SELECTABLE,
                    width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH,
                    editable=True,
                    items=items
                ))
            else:
                bind = proj.bindings[setting['type']]
                if bind.type == const.BIND_TYPE_FIXED:
                    result.append(CellItem(
                        column_name=field.column_name,
                        display_name=field.display_name,
                        width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH,
                        editable=False,
                        fixed_value=bind.value
                    ))
                elif bind.type == const.BIND_TYPE_CALL:
                    result.append(CellItem(
                        column_name=field.column_name,
                        display_name=field.display_name,
                        width=setting['width'] if 'width' in setting else const.DEFAULT_WIDTH,
                        editable=False,
                        call_value=bind.value
                    ))
        else:
            result.append(CellItem(
                column_name=field.column_name,
                display_name=field.display_name
            ))
    return result


def exclude_names(items: list[tuple[str, Any]]) -> dict[str, Any]:
    '''
    column_name, display_nameを除外した辞書を生成する。
    '''
    return {key: value for key, value in items if key not in ['column_name', 'display_name']}


def adjust_column_value(col: GridColumn, value: Any, fixed: bool = False) -> Any:
    '''
    valueの中にフィールドのキーがなかったら、値を補完する。
    fixedがTrueの場合には、fixed_valueを優先する。
    '''
    if fixed and col.fixed_value is not None:
        return col.fixed_value
    if col.field in value:
        return value[col.field]
    if col.fixed_value is not None:
        return col.fixed_value
    if col.call_value is not None:
        if col.call_value == const.CALL_TYPE_UUID:
            return str(uuid4())
    return ''


def make_one_row(columns: list[GridColumn], data: Any, *, need_id: bool = True, fixed: bool = False, segment: tuple = (False, None, None)) -> dict[str, Any]:
    '''
    1行分のデータを生成する。
    '''
    row = {
        col.field: adjust_column_value(col, data, fixed)
        for col in columns
    }

    # セグメントがある場合には、セグメントの値を設定する
    if segment[0]:
        row[segment[1]] = segment[2]

    # idが必要な場合には、idを生成する
    if need_id and 'id' not in row:
        row['id'] = str(uuid4())

    return row


def get_axis_items(proj: Project, map: Mapping, settings: dict[str, object], axis: str, ins: str) -> list[ListItem]:
    items = None
    setting = settings[axis]
    if setting['type'] == const.BIND_TYPE_REFS:
        id = setting['id']
        ins = setting['instance']
        tbl = setting['table']
        items = load_for_select_items(proj.folder, id, ins, tbl)
    if items is None:
        raise RuntimeError(f'No Data for axis. ({ins}@{axis})')
    return items
