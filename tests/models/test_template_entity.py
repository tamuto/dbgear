import unittest

from dbgear.models.project import Project
from dbgear.models.template import entity
from dbgear.models import const

FOLDER_PATH = './etc/test'


class TestTemplate(unittest.TestCase):

    def test_entity_items(self):
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        items = entity.items(proj.schemas, proj.folder, 'test1')
        self.assertEqual(len(items), 1)

        invert_items = entity.items(proj.schemas, proj.folder, 'test1', exist=False)
        self.assertEqual(len(invert_items), 4)

    def test_entity_get(self):
        # データなしの定義のみ読み込み
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        dm, table, info = entity.get(proj.bindings, proj.schemas, proj.folder, 'test1', 'main', 'test_table')

        self.assertEqual(dm.id, 'test1')
        self.assertEqual(dm.instance, 'main')
        self.assertEqual(dm.table_name, 'test_table')
        self.assertEqual(dm.layout, const.LAYOUT_TABLE)
        self.assertEqual(table.table_name, 'test_table')
        self.assertEqual(len(info.grid_columns), 5)
        self.assertEqual(info.grid_rows, [])

    # TODO saveメソッド
    # TODO 1行データ取得？datagrid側かも？
