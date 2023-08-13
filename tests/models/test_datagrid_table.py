import unittest

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.models.environ import entity
from dbgear.models import const

FOLDER_PATH = './etc/test'


class TestDataGrid(unittest.TestCase):

    def test_test_table(self):
        # 通常の単一テーブル
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test2')

        dm, _, info = entity.get(proj, map, 'main', 'test_table')

        self.assertEqual(dm.layout, const.LAYOUT_TABLE)
        self.assertEqual(len(info.grid_columns), 5)
        self.assertEqual(len(info.grid_rows), 2)

    def test_tbl_child(self):
        # 外部リレーションがあるテーブル
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test2')

        dm, _, info = entity.get(proj, map, 'main', 'tbl_child')

        self.assertEqual(dm.layout, const.LAYOUT_TABLE)
        self.assertEqual(len(info.grid_columns), 5)
        self.assertEqual(info.grid_columns[1].field, 'col_id')
        self.assertEqual(len(info.grid_columns[1].items), 2)
        self.assertEqual(info.grid_columns[1].items[0]['caption'], 'P001')
        self.assertEqual(info.grid_columns[1].items[0]['value'], '001')
        self.assertEqual(info.grid_columns[1].items[1]['caption'], 'P002')
        self.assertEqual(info.grid_columns[1].items[1]['value'], '002')
        self.assertEqual(len(info.grid_rows), 4)
