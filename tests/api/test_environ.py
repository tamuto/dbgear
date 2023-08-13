import unittest

from unittest.mock import MagicMock

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.api import environs
from dbgear.api.dtos import NewMapping

FOLDER_PATH = './dist/test'


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
        self.assertEqual(len(result.data), 2)

    def test_create_mapping(self):
        result = environs.create_mapping('test3', NewMapping(
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

    # TODO save
