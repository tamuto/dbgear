from dataclasses import dataclass

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from ..schema import find_field
from ..fileio import load_data
from ..fileio import load_model
from ..fileio import get_data_model_name
from .. import const

from .data import DataModel
from .data import GridColumn


def make_grid_column(
        column_name: str,
        display_name: str,
        *,
        type: str = const.FIELD_TYPE_STRING,
        width: int = 150,
        editable: bool = True,
        hide: bool = False,
        items: list | None = None,
        fixed_value: str | None = None,
        call_value: str | None = None,
        reference: str | None = None):
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
        reference=reference
    )


def load_for_select_items(folder: str, map: Mapping, ins: str, ref: str):
    items = load_data(folder, map.id, ins, ref, True)
    if items is None:
        if map.parent is not None:
            items = load_for_select_items(folder, map.parent, ins, ref)
    else:
        # データが見つかった場合には、DataModelをロードし、
        # caption, valueのデータを生成する
        dm: DataModel = load_model(
            get_data_model_name(folder, map.id, ins, ref),
            DataModel,
            id=map.id,
            instance=ins,
            table_name=ref
        )
        if dm.caption is not None and dm.value is not None:
            items = [{
                'caption': item[dm.caption],
                'value': item[dm.value]
            } for item in items]
        else:
            raise RuntimeError('Invalid Data Model for Master Data.')
    return items


@dataclass
class CellItem:
    column_name: str
    display_name: str
    type: str = const.FIELD_TYPE_STRING
    editable: bool = True
    items: list[object] | None = None
    fixed_value: str | None = None
    call_value: str | None = None
    reference: str | None = None


def make_cell_item(proj: Project, map: Mapping, dm: DataModel, table: Table) -> list[CellItem]:
    result = []
    for cell in dm.cells:
        field = find_field(table.fields, cell)
        if cell in dm.settings:
            setting = dm.settings[cell]
            if setting['type'] == const.BIND_TYPE_FOREIGN_KEY:
                items = load_for_select_items(proj.folder, map, dm.instance, setting['value'])

                result.append(CellItem(
                    column_name=field.column_name,
                    display_name=field.display_name,
                    type=const.FIELD_TYPE_SELECTABLE,
                    editable=True,
                    items=items
                ))
            elif setting['type'] == const.BIND_TYPE_EMBEDDED_DATA:
                result.append(CellItem(
                    column_name=field.column_name,
                    display_name=field.display_name,
                    type=const.FIELD_TYPE_SELECTABLE,
                    editable=True,
                    items=setting['values']
                ))
            elif setting['type'] == const.BIND_TYPE_REF_ID:
                result.append(CellItem(
                    column_name=field.column_name,
                    display_name=field.display_name,
                    type=const.FIELD_TYPE_STRING,
                    editable=False,
                    reference='id'
                ))
            else:
                bind = proj.bindings[setting['type']]
                if bind.type == const.BIND_TYPE_FIXED:
                    result.append(CellItem(
                        column_name=field.column_name,
                        display_name=field.display_name,
                        editable=False,
                        fixed_value=bind.value
                    ))
                elif bind.type == const.BIND_TYPE_CALL:
                    result.append(CellItem(
                        column_name=field.column_name,
                        display_name=field.display_name,
                        editable=False,
                        call_value=bind.value
                    ))
                elif bind.type == const.BIND_TYPE_SELECTABLE:
                    result.append(CellItem(
                        column_name=field.column_name,
                        display_name=field.display_name,
                        items=bind.items
                    ))
        else:
            result.append(CellItem(
                column_name=field.column_name,
                display_name=field.display_name
            ))
    return result
