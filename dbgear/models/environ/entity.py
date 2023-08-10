import os

from ..project import Binding
from ..schema import Schema
from ..schema import Table
from ..fileio import load_model
from ..fileio import save_model
from ..fileio import load_data
from ..fileio import get_data_model_name
from ..datagrid import grid
from ..datagrid.data import DataInfo
from ..datagrid.data import DataModel

from . import mapping


def get(bindings: dict[str, Binding], schemas: dict[str, Schema], folder: str, id: str, ins: str, tbl: str) -> tuple[DataModel, Table, DataInfo]:
    dm = load_model(
        get_data_model_name(folder, id, ins, tbl),
        DataModel,
        id=id,
        instance=ins,
        table_name=tbl
    )
    table = schemas[ins].get_table(tbl)
    data = load_data(folder, id, ins, tbl)
    info = grid.build(folder, bindings, dm, table, data)

    return (dm, table, info)


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


def save(folder: str, id: str, ins: str, tbl: str, data: DataModel) -> None:
    save_model(
        get_data_model_name(folder, id, ins, tbl),
        data
    )


def save_data(schemas: dict[str, Schema], folder: str, id: str, ins: str, tbl: str, rows: object) -> None:
    dm = load_model(get_data_model_name(folder, id, ins, tbl), DataModel)
    table = schemas[ins].get_table(tbl)
    data = grid.parse(dm, table, rows)
    # save_yaml(
    #     get_data_rawname(folder, id, ins, tbl),
    #     data
    # )

# def build_new_data_row(self, id, instance, table_name):
#     config = self._read_template_data_config(id, instance, table_name)
#     row = grid.new_data_row(self.project, config)
#     return row
