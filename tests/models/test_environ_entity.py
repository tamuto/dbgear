import unittest

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.models.environ import entity
from dbgear.models import const

FOLDER_PATH = './etc/test'


class TestEnviron(unittest.TestCase):

    def test_entity_items(self):
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        items = entity.items(proj.schemas, proj.folder, 'test1')
        self.assertEqual(len(items), 1)

        invert_items = entity.items(proj.schemas, proj.folder, 'test1', exist=False)
        self.assertEqual(len(invert_items), 6)

    def test_entity_get(self):
        # データなしの定義のみ読み込み
        # および、親経由のデータの参照
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test1')

        dm, table, info = entity.get(proj, map, 'main', 'tbl_child')

        self.assertEqual(dm.id, 'test1')
        self.assertEqual(dm.instance, 'main')
        self.assertEqual(dm.table_name, 'tbl_child')
        self.assertEqual(dm.layout, const.LAYOUT_TABLE)
        self.assertEqual(len(dm.settings), 3)
        self.assertEqual(dm.settings['update_date']['type'], 'now')
        self.assertEqual(table.table_name, 'tbl_child')
        self.assertEqual(len(info.grid_columns), 5)
        self.assertEqual(info.grid_columns[1].field, 'col_id')
        self.assertEqual(len(info.grid_columns[1].items), 2)
        self.assertEqual(info.grid_columns[1].items[0]['caption'], 'P001')
        self.assertEqual(info.grid_columns[1].items[0]['value'], '001')
        self.assertEqual(info.grid_columns[1].items[1]['caption'], 'P002')
        self.assertEqual(info.grid_columns[1].items[1]['value'], '002')
        self.assertEqual(info.grid_rows, [])

    # TODO saveメソッド
    # TODO 1行データ取得？datagrid側かも？
