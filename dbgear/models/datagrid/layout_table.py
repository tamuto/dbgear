from typing import Any
from uuid import uuid4

from ..project import Binding
from ..schema import Table
from ..schema import Field
from ..fileio import load_data
from .. import const

from .data import DataModel
from .data import DataInfo
from .data import GridColumn


def build(folder: str, bindings: dict[str, Binding], dm: DataModel, table: Table, data: Any) -> DataInfo:
    # FIXME 複合キー型のforegin_key
    columns = [
        _make_table_grid_column(folder, bindings, field, dm)
        for field in table.fields
    ]
    return DataInfo(
        grid_columns=columns,
        grid_rows=data
    )


def _make_table_grid_column(folder: str, bindings: dict[str, Binding], field: Field, dm: DataModel):
    if field.foreign_key:
        # FIXME ID列とキャプション列を生成する？
        items = load_data(folder, dm.id, dm.instance, field.foreign_key)
        return GridColumn(
            field=field.column_name,
            type='singleSelect',
            header_name=field.display_name,
            width=150,
            editable=True,
            items=items
        )
    if field.column_name in dm.settings:
        setting = dm.settings[field.column_name]
        data = bindings[setting]
        if data.type == const.BIND_TYPE_FIXED:
            return GridColumn(
                field=field.column_name,
                type='string',
                header_name=field.display_name,
                width=150,
                editable=False,
                hide=True
            )
        if data.type == const.BIND_TYPE_CALL:
            return GridColumn(
                field=field.column_name,
                type='string',
                header_name=field.display_name,
                width=150,
                editable=False
            )
        if data.type == const.BIND_TYPE_SELECTABLE:
            return GridColumn(
                field=field.column_name,
                type='singleSelect',
                header_name=field.display_name,
                width=150,
                editable=True,
                items=data.items
            )
    return GridColumn(
        field=field.column_name,
        type='string',
        header_name=field.display_name,
        width=150,
        editable=True
    )


def new_data_row(table):
    row = {
        'id': uuid4()
    }
    row.update({field.column_name: '' for field in table.fields})
    return row
