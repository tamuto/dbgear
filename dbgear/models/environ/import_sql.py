from ..project import Project
from ..environ.data import Mapping
from ..datagrid.data import DataModel
from ..datagrid import layout_table
from ..datagrid import column
from ..fileio import load_model
from ..fileio import save_yaml
from ..fileio import get_data_model_name
from ..fileio import get_data_dat_name

from ...dbio import engine


def execute(proj: Project, map: Mapping, ins: str, tbl: str, seg: str | None, host: str, sql: str):
    dm = load_model(
        get_data_model_name(proj.folder, map.id, ins, tbl),
        DataModel,
        id=map.id,
        instance=ins,
        table_name=tbl
    )
    columns, seg_info = layout_table.build_columns(proj, map, dm, proj.schemas[ins].get_table(tbl))
    with engine.get_connection(proj.deployments[host]) as conn:
        data = engine.select_all(conn, sql)

    if seg_info is None:
        rows = [column.make_one_row(columns, d, need_id=False, fixed=True) for d in data]
    else:
        # seg_infoがある場合には、segの引数は指定されている必要がある。
        assert seg is not None
        rows = [column.make_one_row(columns, d, need_id=False, fixed=True, segment=(True, seg_info[0], seg)) for d in data]

    save_yaml(
        get_data_dat_name(proj.folder, map.id, ins, tbl, seg),
        rows
    )
