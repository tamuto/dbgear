from uuid import uuid4

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import Field
from .. import const

from .data import DataModel
from .data import DataInfo
from . import column


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: list) -> DataInfo:
    # フィールドを設定に従って展開する。ForeignKeyなども設定に含まれるものとする。
    columns = []
    for field in table.fields:
        if field.column_name in dm.settings:
            grid_column = _make_grid_column_from_setting(proj, map, dm, field)
        else:
            grid_column = column.make_grid_column(field)

        columns.append(grid_column)

    return DataInfo(
        grid_columns=columns,
        grid_rows=data
    )


def _make_grid_column_from_setting(proj: Project, map: Mapping, dm: DataModel, field: Field):
    setting = dm.settings[field.column_name]
    if setting['type'] == const.BIND_TYPE_REF_ID:
        # 固定値と同じものとする
        return column.make_grid_column(field, editable=False, hide=True)
    if setting['type'] == const.BIND_TYPE_FOREIGN_KEY:
        # 選択肢は外部データを参照する以外は選択型と同じ
        items = column.load_for_select_items(proj.folder, map, dm.instance, setting['value'])
        if items is None:
            # データが見つからなければ空の配列とする
            items = []
        return column.make_grid_column(field, items=items)

    data =  proj.bindings[setting['type']]
    if data.type == const.BIND_TYPE_FIXED:
        return column.make_grid_column(field, editable=False, hide=True)
    if data.type == const.BIND_TYPE_CALL:
        return column.make_grid_column(field, editable=False)
    if data.type == const.BIND_TYPE_SELECTABLE:
        return column.make_grid_column(field, items=data.items)
    raise RuntimeError('Unknown Data Type')


def new_data_row(table):
    row = {
        'id': uuid4()
    }
    row.update({field.column_name: '' for field in table.fields})
    return row
