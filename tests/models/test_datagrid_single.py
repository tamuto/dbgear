import unittest

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.models.environ import entity
from dbgear.models.datagrid import grid
from dbgear.models.datagrid.data import DataModel
from dbgear.models.fileio import load_model
from dbgear.models.fileio import get_data_model_name
from dbgear.models import const

FOLDER_PATH = './etc/test'


class TestDataGrid(unittest.TestCase):

    def test_tbl_matrix(self):
        # 単票テーブル
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test2')

        dm, _, info = entity.get(proj, map, 'main', 'properties')

        self.assertEqual(dm.layout, const.LAYOUT_SINGLE)
        self.assertEqual(len(info.grid_columns), 2)
        self.assertEqual(info.grid_columns[1].field, 'value')
        self.assertEqual(info.grid_columns[1].header_name, '値')
        self.assertEqual(len(info.grid_rows), 2)

    def test_parse(self):
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test2')
        ins = 'main'
        tbl = 'properties'

        dm = load_model(
            get_data_model_name(proj.folder, map.id, ins, tbl),
            DataModel,
            id=map.id,
            instance=ins,
            table_name=tbl,
        )
        table = proj.schemas[ins].get_table(tbl)

        rows = [
            {'key': 'AAA', 'value': 111, 'id': 'ef9e0e9a-e077-4f17-b899-71165ca738f3'},
            {'key': 'BBB', 'value': '', 'id': '7cb5e0d2-7cc2-4f97-b524-846e30492d4e'},
            {'key': 'CCC', 'value': 333, 'id': 'e08ff4d1-10fb-4c61-b4c2-cb22629379ad'},
            {'key': 'DDD', 'value': '', 'id': 'b2efc38a-f02b-41c7-8122-78c7bd68ba0c'}
        ]

        data = grid.parse(proj, map, dm, table, rows)
        self.assertEqual(len(data), 4)
        self.assertEqual(data[0]['value'], 111)
