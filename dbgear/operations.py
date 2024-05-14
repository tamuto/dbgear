from logging import getLogger
from datetime import datetime
from .dbio import engine
from .dbio import database
from .dbio import table

from .models.project import Project
from .models.environ import mapping
from .models.environ.data import Mapping
from .models.datagrid.data import DataModel
from .models.fileio import load_all_data
from .models.fileio import get_data_model_name
from .models.fileio import is_exist_data_model
from .models.fileio import load_model

logger = getLogger(__name__)


def _load_for_entry(folder: str, map: Mapping, ins: str, tbl: str):
    # 自身のデータをロードし、存在しなければ親を再帰的に遡ってロードする。
    items = load_all_data(folder, map.id, ins, tbl)
    if items is None:
        if map.parent is not None:
            items = _load_for_entry(folder, map.parent, ins, tbl)
    return items


def _is_update_diff(proj: Project, map: Mapping, ins: str, tbl: str) -> bool:
    if is_exist_data_model(proj.folder, map.id, ins, tbl) is False:
        if map.parent is None:
            return False
        return _is_update_diff(proj, map.parent, ins, tbl)

    dm = load_model(
        get_data_model_name(proj.folder, map.id, ins, tbl),
        DataModel,
        id=map.id,
        instance=ins,
        table_name=tbl
    )
    return dm.sync_mode == 'update_diff'


class Operation:

    @staticmethod
    def get_instance(folder: str, env: str, deploy: str):
        project = Project(folder)
        project.read_definitions()
        return Operation(project, env, deploy)

    def __init__(self, project: Project, env: str, deploy: str):
        self.project = project
        self.map = mapping.get(project.folder, env)
        self.conn = engine.get_connection(project.deployments[deploy])
        self.ymd = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def create_database(self, all: str):
        if all == 'drop':
            logger.info(f'database {self.map.id}')
            if database.is_exist(self.conn, self.map.id):
                database.drop(self.conn, self.map.id)
            database.create(self.conn, self.map.id)
        else:
            # 差分更新または個別指定の場合で、データベースが存在しない場合は作成する。
            if not database.is_exist(self.conn, self.map.id):
                logger.info(f'database {self.map.id} was created.')
                database.create(self.conn, self.map.id)

    def create_table(self, all: str, target: str):
        for ins in self.map.instances:
            schema = self.project.schemas[ins]
            for tbl in schema.tables.values():
                if not all and target != tbl.table_name:
                    continue
                # テーブルが存在しない場合は作成する。
                if table.is_exist(self.conn, self.map.id, tbl) is False:
                    logger.info(f'table {self.map.id}.{tbl.table_name} was created.')
                    table.create(self.conn, self.map.id, tbl)
                    continue
                # データのバックアップ
                logger.info(f'backup {self.map.id}.{tbl.table_name}')
                table.backup(self.conn, self.map.id, tbl, self.ymd)
                # テーブルの再作成
                logger.info(f'drop & create table {self.map.id}.{tbl.table_name}')
                table.drop(self.conn, self.map.id, tbl)
                table.create(self.conn, self.map.id, tbl)

    def insert_data(self, all: bool, target: str):
        # データ投入
        for ins in self.map.instances:
            schema = self.project.schemas[ins]
            for tbl in schema.tables.values():
                if not all and target != tbl.table_name:
                    continue
                items = _load_for_entry(self.project.folder, self.map, ins, tbl.table_name)
                if items is not None:
                    logger.info(f'insert {self.map.id}.{tbl.table_name}')
                    table.insert(self.conn, self.map.id, tbl, items)
                if _is_update_diff(self.project, self.map, ins, tbl.table_name):
                    # 新規作成時にはバックアップはない
                    if table.is_exist_backup(self.conn, self.map.id, tbl, self.ymd):
                        # バックアップからデータを復元
                        # create_tableの中で再作成されているため
                        logger.info(f'restore {self.map.id}.{tbl.table_name}')
                        table.restore(self.conn, self.map.id, tbl, self.ymd)

    def reset_all(self):
        # ユニットテストなど一括して再作成を行う場合に使用する。
        self.create_database('drop')
        self.create_table('drop', None)

    def require(self, instance: str, table_name: str):
        # ユニットテストなどで指定したデータを挿入する。
        schema = self.project.schemas[instance]
        tbl = schema.get_table(table_name)
        # TODO 将来的なバージョンでは差分チェックか否かの判定を行う。
        items = _load_for_entry(self.project.folder, self.map, instance, table_name)
        if items is not None:
            logger.info(f'insert {self.map.id}.{table_name}')
            table.insert(self.conn, self.map.id, tbl, items)


def apply(project, env: str, target: str, all: str, deploy: str):
    with Operation(project, env, deploy) as op:
        op.create_database(all)
        op.create_table(all, target)
        op.insert_data(all, target)
