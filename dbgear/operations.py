from logging import getLogger
from .dbio import engine
from .dbio import database
from .dbio import table

from .models.environ import mapping
from .models.environ.data import Mapping
from .models.fileio import load_data

logger = getLogger(__name__)


def _load_for_entry(folder: str, map: Mapping, ins: str, tbl: str):
    # 自身のデータをロードし、存在しなければ親を再帰的に遡ってロードする。
    items = load_data(folder, map.id, ins, tbl, True)
    if items is None:
        if map.parent is not None:
            items = _load_for_entry(folder, map.parent, ins, tbl)
    return items


def apply(project, env, deploy):
    map = mapping.get(project.folder, env)
    with engine.get_connection(project.deployments[deploy]) as conn:
        # データベース作成
        logger.info(f'database {map.id}')
        if database.is_exist(conn, map.id):
            database.drop(conn, map.id)
        database.create(conn, map.id)
        # database.create_user(conn, 'test', '%', 'test')
        # database.grant(conn, env, 'test', '%')

        # テーブル作成
        for ins in map.instances:
            schema = project.schemas[ins]
            for tbl in schema.tables.values():
                logger.info(f'table {map.id}.{tbl.table_name}')
                table.create(conn, map.id, tbl)

        # データ投入
        for ins in map.instances:
            schema = project.schemas[ins]
            for tbl in schema.tables.values():
                items = _load_for_entry(project.folder, map, ins, tbl.table_name)
                if items is not None:
                    logger.info(f'insert {map.id}.{tbl.table_name}')
                    table.insert(conn, map.id, tbl, items)
