from ..project import Project
from ..environ.data import Mapping
from ..datagrid.data import DataModel
from ..datagrid.layout_table import build_columns
from ..datagrid.column import build_one_row
from ..fileio import load_model
from ..fileio import save_yaml
from ..fileio import get_data_model_name
from ..fileio import get_data_dat_name

from ...dbio import engine


def execute(proj: Project, map: Mapping, ins: str, tbl: str, host: str, sql: str):
    dm = load_model(
        get_data_model_name(proj.folder, map.id, ins, tbl),
        DataModel,
        id=map.id,
        instance=ins,
        table_name=tbl
    )
    columns = build_columns(proj, map, dm, proj.schemas[ins].get_table(tbl))
    with engine.get_connection(proj.deployments[host]) as conn:
        data = engine.select_all(conn, sql)
    rows = [build_one_row(columns, d, fixed=True) for d in data]

    save_yaml(
        get_data_dat_name(proj.folder, map.id, ins, tbl),
        rows
    )
