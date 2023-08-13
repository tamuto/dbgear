from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from .. import const

from .data import DataModel
from .data import DataInfo
from . import layout_table
from . import layout_matrix
from . import layout_single


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, data: list) -> DataInfo:
    if dm.layout == const.LAYOUT_TABLE:
        return layout_table.build(proj, map, dm, table, data)
    if dm.layout == const.LAYOUT_MATRIX:
        return layout_matrix.build(proj, map, dm, table, data)
    if dm.layout == const.LAYOUT_SINGLE:
        return layout_single.build(proj, map, dm, table, data)

def parse():
    pass
