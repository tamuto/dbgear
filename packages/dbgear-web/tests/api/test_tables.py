import unittest

from unittest.mock import MagicMock

from dbgear.core.models.project import Project
from dbgear_web.api import tables

FOLDER_PATH = '../../etc/test'


class TestTables(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        self.request = MagicMock()
        self.request.app.state.project = proj

    def test_get_tables(self):
        result = tables.get_tables(self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(len(result.data['main']), 8)

    def test_get_table(self):
        result = tables.get_table('main', 'test_table', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data.table_name, 'test_table')
