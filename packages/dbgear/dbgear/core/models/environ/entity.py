import os

from ..project import Project
from ..environ.data import Mapping
from ..schema import Schema
from ..schema import Table
from ..fileio import load_model
from ..fileio import save_model
from ..fileio import save_yaml
from ..fileio import get_data_model_name
from ..fileio import get_data_dat_name
from ..datagrid import grid
from ..datagrid.data import DataInfo
from ..datagrid.data import DataModel

from . import mapping


def get(proj: Project, map: Mapping, ins: str, tbl: str, seg: str | None) -> tuple[DataModel, Table, DataInfo]:
    dm = load_model(
        get_data_model_name(proj.folder, map.id, ins, tbl),
        DataModel,
        id=map.id,
        instance=ins,
        table_name=tbl
    )
    table = proj.schemas[ins].get_table(tbl)
    info = grid.build(proj, map, dm, table, seg)

    return (dm, table, info)


def get_row(proj: Project, map: Mapping, ins: str, tbl: str) -> dict[str, object]:
    dm = load_model(
        get_data_model_name(proj.folder, map.id, ins, tbl),
        DataModel,
        id=map.id,
        instance=ins,
        table_name=tbl
    )
    table = proj.schemas[ins].get_table(tbl)
    row = grid.build_one_row(proj, map, dm, table)
    return row


def get_description(proj: Project, id: str, ins: str, tbl: str) -> str:
    return load_model(
        get_data_model_name(proj.folder, id, ins, tbl),
        DataModel,
        id=id,
        instance=ins,
        table_name=tbl
    ).description


def items(schemas: dict[str, Schema], folder: str, id: str, *, exist: bool = True) -> list[tuple[str, Table]]:
    config = mapping.get(folder, id)
    tables = []
    for ins in config.instances:
        if ins not in schemas:
            # 元の定義から消えているため無視する。
            continue
        tables.extend([
            (ins, tbl)
            for tbl in schemas[ins].get_tables().values()
            if is_exist(folder, id, ins, tbl.table_name) == exist
        ])
    return sorted(tables, key=lambda x: f'{x[0]}@{x[1].table_name}')


def is_exist(folder: str, id: str, ins: str, tbl: str) -> bool:
    return os.path.isfile(get_data_model_name(folder, id, ins, tbl))


def save(proj: Project, map: Mapping, ins: str, tbl: str, data: DataModel) -> None:
    save_model(
        get_data_model_name(proj.folder, map.id, ins, tbl),
        data,
        ['id', 'instance', 'table_name']
    )


def save_data(proj: Project, map: Mapping, ins: str, tbl: str, seg: str | None, rows: object) -> None:
    dm = load_model(
        get_data_model_name(proj.folder, map.id, ins, tbl),
        DataModel,
        id=map.id,
        instance=ins,
        table_name=tbl
    )
    table = proj.schemas[ins].get_table(tbl)
    data = grid.parse(proj, map, dm, table, seg, rows)
    save_yaml(
        get_data_dat_name(proj.folder, map.id, ins, tbl, seg),
        data
    )
