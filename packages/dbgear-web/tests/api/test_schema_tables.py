import unittest
from unittest.mock import MagicMock, patch

from dbgear.core.models.project import Project
from dbgear.core.models.schema import Table, Schema
from dbgear_web.api import schema_tables
from dbgear_web.api.dtos import CreateTableRequest

FOLDER_PATH = '../../etc/test'


class TestSchemaTables(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        
        self.request = MagicMock()
        self.request.app.state.project = proj

    def tearDown(self) -> None:
        pass

    @patch('dbgear_web.api.schema_tables.SchemaManager')
    @patch('dbgear_web.api.schema_tables.project')
    def test_get_tables_empty(self, mock_project, mock_schema_manager):
        """空のスキーマでテーブル一覧を取得"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        mock_schema = Schema('test_schema')
        mock_manager.get_schema.return_value = mock_schema
        
        result = schema_tables.get_tables('test_schema', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data, [])

    @patch('dbgear_web.api.schema_tables.SchemaManager')
    @patch('dbgear_web.api.schema_tables.project')
    def test_get_tables_nonexistent_schema(self, mock_project, mock_schema_manager):
        """存在しないスキーマでテーブル一覧取得エラー"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = False
        
        with self.assertRaises(Exception) as context:
            schema_tables.get_tables('nonexistent', self.request)
        self.assertIn('not found', str(context.exception))

    @patch('dbgear_web.api.schema_tables.SchemaManager')
    @patch('dbgear_web.api.schema_tables.project')
    def test_create_table(self, mock_project, mock_schema_manager):
        """新規テーブルを作成"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        table_request = CreateTableRequest(
            instance='test_instance',
            table_name='test_table',
            display_name='Test Table'
        )
        result = schema_tables.create_table('test_schema', self.request, table_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('created successfully', result.message)
        mock_manager.add_table.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_tables.SchemaManager')
    @patch('dbgear_web.api.schema_tables.project')
    def test_get_table(self, mock_project, mock_schema_manager):
        """特定テーブルの詳細を取得"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_table = Table(
            instance='test_instance',
            table_name='test_table',
            display_name='Test Table',
            fields=[],
            indexes=[]
        )
        mock_manager.get_table.return_value = mock_table
        
        result = schema_tables.get_table('test_schema', 'test_table', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data.table_name, 'test_table')
        self.assertEqual(result.data.display_name, 'Test Table')

    @patch('dbgear_web.api.schema_tables.SchemaManager')
    @patch('dbgear_web.api.schema_tables.project')
    def test_get_nonexistent_table(self, mock_project, mock_schema_manager):
        """存在しないテーブルの取得でエラー"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        mock_manager.get_table.return_value = None
        
        with self.assertRaises(Exception) as context:
            schema_tables.get_table('test_schema', 'nonexistent', self.request)
        self.assertIn('not found', str(context.exception))

    @patch('dbgear_web.api.schema_tables.SchemaManager')
    @patch('dbgear_web.api.schema_tables.project')
    def test_update_table(self, mock_project, mock_schema_manager):
        """テーブルを更新"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_existing_table = Table(
            instance='test_instance',
            table_name='test_table',
            display_name='Original Name',
            fields=[],
            indexes=[]
        )
        mock_manager.get_table.return_value = mock_existing_table
        
        update_request = CreateTableRequest(
            instance='test_instance',
            table_name='test_table',
            display_name='Updated Name'
        )
        result = schema_tables.update_table('test_schema', 'test_table', self.request, update_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('updated successfully', result.message)
        mock_manager.update_table.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_tables.SchemaManager')
    @patch('dbgear_web.api.schema_tables.project')
    def test_delete_table(self, mock_project, mock_schema_manager):
        """テーブルを削除"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_table = Table(
            instance='test_instance',
            table_name='test_table',
            display_name='Test Table',
            fields=[],
            indexes=[]
        )
        mock_manager.get_table.return_value = mock_table
        
        result = schema_tables.delete_table('test_schema', 'test_table', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertIn('deleted successfully', result.message)
        mock_manager.delete_table.assert_called_once()
        mock_manager.save.assert_called_once()


if __name__ == '__main__':
    unittest.main()