from ..schema import Field
from ..environ.data import Mapping
from ..fileio import load_data
from ..fileio import load_model
from ..fileio import get_data_model_name
from .. import const

from .data import DataModel
from .data import GridColumn


def make_grid_column(
        field: Field,
        *,
        type: str = const.FIELD_TYPE_STRING,
        width: int = 150,
        editable: bool = True,
        hide: bool = False,
        items: list | None = None):
    return GridColumn(
        field=field.column_name,
        type=type,
        header_name=field.display_name,
        width=width,
        editable=editable,
        hide=hide,
        items=items
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
        items = [{
            'caption': item[dm.caption],
            'value': item[dm.value]
        } for item in items]
    return items
