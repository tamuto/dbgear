import unittest

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.models.environ import entity
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
        self.assertEqual(len(info.grid_rows), 4)
