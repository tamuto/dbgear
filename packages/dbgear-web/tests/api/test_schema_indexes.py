import unittest
from unittest.mock import MagicMock, patch

from dbgear.core.models.project import Project
from dbgear.core.models.schema import Table, Field, Index
from dbgear_web.api import schema_indexes
from dbgear_web.api.dtos import CreateIndexRequest

FOLDER_PATH = '../../etc/test'


class TestSchemaIndexes(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        
        self.request = MagicMock()
        self.request.app.state.project = proj

    def tearDown(self) -> None:
        pass

    @patch('dbgear_web.api.schema_indexes.SchemaManager')
    @patch('dbgear_web.api.schema_indexes.project')
    def test_get_indexes_empty(self, mock_project, mock_schema_manager):
        """空のテーブルでインデックス一覧を取得"""
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
        
        result = schema_indexes.get_indexes('test_schema', 'test_table', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data, [])

    @patch('dbgear_web.api.schema_indexes.SchemaManager')
    @patch('dbgear_web.api.schema_indexes.project')
    def test_create_index_with_name(self, mock_project, mock_schema_manager):
        """インデックス名指定でインデックスを作成"""
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
        
        index_request = CreateIndexRequest(
            index_name='idx_test_name',
            columns=['name']
        )
        result = schema_indexes.create_index('test_schema', 'test_table', self.request, index_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('created successfully', result.message)
        mock_manager.add_index.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_indexes.SchemaManager')
    @patch('dbgear_web.api.schema_indexes.project')
    def test_create_index_auto_name(self, mock_project, mock_schema_manager):
        """インデックス名自動生成でインデックスを作成"""
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
        
        index_request = CreateIndexRequest(
            columns=['email']
        )
        result = schema_indexes.create_index('test_schema', 'test_table', self.request, index_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('created successfully', result.message)
        mock_manager.add_index.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_indexes.SchemaManager')
    @patch('dbgear_web.api.schema_indexes.project')
    def test_delete_index(self, mock_project, mock_schema_manager):
        """インデックスを削除"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_index = Index(
            index_name='idx_test_delete',
            columns=['name']
        )
        
        mock_table = Table(
            instance='test_instance',
            table_name='test_table',
            display_name='Test Table',
            fields=[],
            indexes=[mock_index]
        )
        mock_manager.get_table.return_value = mock_table
        
        result = schema_indexes.delete_index('test_schema', 'test_table', 'idx_test_delete', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertIn('deleted successfully', result.message)
        mock_manager.delete_index.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_indexes.SchemaManager')
    @patch('dbgear_web.api.schema_indexes.project')
    def test_delete_nonexistent_index(self, mock_project, mock_schema_manager):
        """存在しないインデックスの削除でエラー"""
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
            indexes=[]  # 空のインデックスリスト
        )
        mock_manager.get_table.return_value = mock_table
        
        with self.assertRaises(Exception) as context:
            schema_indexes.delete_index('test_schema', 'test_table', 'nonexistent', self.request)
        self.assertIn('not found', str(context.exception))

    @patch('dbgear_web.api.schema_indexes.SchemaManager')
    @patch('dbgear_web.api.schema_indexes.project')
    def test_get_indexes_with_data(self, mock_project, mock_schema_manager):
        """インデックスが存在するテーブルでインデックス一覧を取得"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_index1 = Index(index_name='idx_name', columns=['name'])
        mock_index2 = Index(index_name='idx_email', columns=['email'])
        
        mock_table = Table(
            instance='test_instance',
            table_name='test_table',
            display_name='Test Table',
            fields=[],
            indexes=[mock_index1, mock_index2]
        )
        mock_manager.get_table.return_value = mock_table
        
        result = schema_indexes.get_indexes('test_schema', 'test_table', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(len(result.data), 2)
        
        # インデックス名を確認
        index_names = [idx['index_name'] for idx in result.data]
        self.assertIn('idx_name', index_names)
        self.assertIn('idx_email', index_names)


if __name__ == '__main__':
    unittest.main()