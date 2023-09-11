from typing import Any

from ..project import Project
from ..environ.data import Mapping
from ..schema import Table
from .. import const

from .data import DataModel
from .data import DataInfo
from . import layout_table
from . import layout_matrix
from . import layout_single


def build(proj: Project, map: Mapping, dm: DataModel, table: Table, segment: str | None) -> DataInfo:
    if dm.layout == const.LAYOUT_TABLE:
        return layout_table.build(proj, map, dm, table, segment)
    if dm.layout == const.LAYOUT_MATRIX:
        return layout_matrix.build(proj, map, dm, table)
    if dm.layout == const.LAYOUT_SINGLE:
        return layout_single.build(proj, map, dm, table)
    raise RuntimeError(f'Unknown layout. {dm.layout}')


def build_one_row(proj: Project, map: Mapping, dm: DataModel, table: Table) -> dict[str, Any]:
    if dm.layout == const.LAYOUT_TABLE:
        return layout_table.build_one_row(proj, map, dm, table)
    # このレイアウトでは行を作成できないの例外を発生させる
    raise RuntimeError('Cannot build one row at this layout.')


def parse(proj: Project, map: Mapping, dm: DataModel, table: Table, segment: str | None, data: Any) -> list[dict[str, Any]]:
    if dm.layout == const.LAYOUT_TABLE:
        return layout_table.parse(proj, map, dm, table, segment, data)
    if dm.layout == const.LAYOUT_MATRIX:
        return layout_matrix.parse(proj, map, dm, table, data)
    if dm.layout == const.LAYOUT_SINGLE:
        return layout_single.parse(proj, map, dm, table, data)
    raise RuntimeError(f'Unknown layout. {dm.layout}')
