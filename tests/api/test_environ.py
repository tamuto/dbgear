import unittest

from unittest.mock import MagicMock

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.api import environs
from dbgear.api.dtos import NewMapping

FOLDER_PATH = './etc/test'


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
        result = environs.get_tables('test2', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(len(result.data), 5)

    def test_get_not_exist_tables(self):
        result = environs.get_not_exist_tables('test2', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(len(result.data), 2)

    def test_get_table(self):
        result = environs.get_table('test2', 'main', 'test_table', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data.model.table_name, 'test_table')

    def test_update_data(self):
        data = [
            {
                'col_id': '001',
                'name': 'P001',
                'num': 1,
                'update_date': 'NOW()',
                'update_user': "'SYSTEM'",
                'id': 'e2e738ee-29d7-4a9d-aa56-2b906ad99cf2'
            },
            {
                'col_id': '002',
                'name': 'P002',
                'num': None,
                'update_date': 'NOW()',
                'update_user': "'SYSTEM'",
                'id': '7b984dd6-ef1f-43d0-8b60-4e4cd4c67db8'
            }
        ]
        result = environs.update_data('test1', 'main', 'test_table', self.request, data)
        self.assertEqual(result.status, 'OK')
