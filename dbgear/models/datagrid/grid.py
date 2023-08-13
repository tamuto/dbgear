from typing import Any

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from .. import const

from .data import DataModel
from .data import DataInfo
from . import layout_table


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: Any) -> DataInfo:
    if dm.layout == const.LAYOUT_TABLE:
        return layout_table.build(proj, map, dm, table, data)


def parse() -> Any:
    pass
