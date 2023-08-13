import unittest

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.models.environ import entity
from dbgear.models import const

FOLDER_PATH = './etc/test'


class TestDataGrid(unittest.TestCase):

    def test_tbl_matrix(self):
        # マトリックステーブル
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test2')

        dm, _, info = entity.get(proj, map, 'main', 'tbl_matrix')

        self.assertEqual(dm.layout, const.LAYOUT_MATRIX)
        self.assertEqual(len(info.grid_columns), 5)
        self.assertEqual(info.grid_columns[1].field, '3f2a4961-4363-4c9e-aba1-8a91f6909be7_value')
        self.assertEqual(info.grid_columns[1].header_name, 'AAA(値)')
        self.assertEqual(len(info.grid_columns[1].items), 2)
        self.assertEqual(len(info.grid_rows), 3)
