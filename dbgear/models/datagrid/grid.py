from typing import Any

from ..project import Binding
from ..schema import Table
from .. import const

from .data import DataModel
from .data import DataInfo
from . import layout_table


def build(bindings: dict[str, Binding], dm: DataModel, table: Table, data: Any) -> DataInfo:
    if dm.layout == const.LAYOUT_TABLE:
        return layout_table.build(bindings, dm, table, data)


def parse() -> Any:
    pass
