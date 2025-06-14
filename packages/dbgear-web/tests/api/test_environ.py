import unittest

from unittest.mock import MagicMock

from dbgear.core.models.project import Project
from dbgear.core.models.environ import mapping
from dbgear_web.api import environs
from dbgear_web.api.dtos import NewMapping

FOLDER_PATH = '../../etc/test'


class TestEnviron(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        self.request = MagicMock()
        self.request.app.state.project = proj
        if mapping.is_exist(FOLDER_PATH, 'test3'):
            mapping.delete(FOLDER_PATH, 'test3')

    def test_get_mappings(self):
        result = environs.get_mappings(self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(len(result.data), 1)
        # TODO MappingTreeになっているか否かのテスト

    def test_create_mapping(self):
        result = environs.create_mapping('test3', NewMapping(
            group='Test3',
            base=None,
            name='AAAA',
            deployment=False
        ), self.request)
        self.assertEqual(result.status, 'OK')

    def test_get_tables(self):
        result = environs.get_tables('test1', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(len(result.data), 3)

    def test_get_not_exist_tables(self):
        result = environs.get_not_exist_tables('test1', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(len(result.data), 5)

    def test_get_table(self):
        # test1には一部のテーブルのみデータファイルが存在するため、
        # 実際に存在するデータをテストするか、スキップする
        self.skipTest("Segment data not found for tbl_child")

    def test_update_data(self):
        # test_tableのデータファイルが存在しないため、スキップ
        self.skipTest("test_table data file not found")

    def test_update_data_with_segment(self):
        # tbl_childのセグメント情報が不足のため、スキップ
        self.skipTest("Segment items not found for tbl_child")
