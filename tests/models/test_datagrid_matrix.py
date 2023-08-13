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
        self.assertEqual(len(info.grid_columns), 4)
        self.assertEqual(info.grid_columns[1].field, 'c744603c-635e-4af8-a48e-b85418e1f569_value')
        self.assertEqual(info.grid_columns[1].header_name, 'Test1(値)')
        self.assertEqual(len(info.grid_columns[1].items), 2)
