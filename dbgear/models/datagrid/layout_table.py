from typing import Any
from uuid import uuid4

from ..project import Binding
from ..schema import Table
from .. import const

from .data import DataModel
from .data import DataInfo
from .data import GridColumns


def build(bindings: dict[str, Binding], dm: DataModel, table: Table, data: Any) -> DataInfo:
    columns = [
        _make_table_grid_column(bindings, field, dm.settings)
        for field in table.fields
    ]
    return DataInfo(
        grid_columns=columns,
        grid_rows=data
    )


def _make_table_grid_column(bindings: dict[str, Binding], field, settings: dict[str, str]):
    if field.column_name in settings:
        setting = settings[field.column_name]
        data = bindings[setting]
        if data.type == const.BIND_TYPE_FIXED:
            return GridColumns(
                field=field.column_name,
                type='string',
                header_name=field.display_name,
                width=150,
                editable=False,
                hide=True
            )
        if data.type == const.BIND_TYPE_CALL:
            return GridColumns(
                field=field.column_name,
                type='string',
                header_name=field.display_name,
                width=150,
                editable=False
            )
        if data.type == const.BIND_TYPE_SELECTABLE:
            return GridColumns(
                field=field.column_name,
                type='singleSelect',
                header_name=field.display_name,
                width=150,
                editable=True,
                items=data.items
            )
    return GridColumns(
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
    row.update({ field.column_name: '' for field in table.fields })
    return row
