import unittest
from unittest.mock import MagicMock, patch

from dbgear.core.models.project import Project
from dbgear.core.models.schema import Table, Field
from dbgear_web.api import schema_fields
from dbgear_web.api.dtos import CreateFieldRequest, UpdateFieldRequest

FOLDER_PATH = '../../etc/test'


class TestSchemaFields(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        
        self.request = MagicMock()
        self.request.app.state.project = proj

    def tearDown(self) -> None:
        pass

    @patch('dbgear_web.api.schema_fields.SchemaManager')
    @patch('dbgear_web.api.schema_fields.project')
    def test_get_fields_empty(self, mock_project, mock_schema_manager):
        """空のテーブルでフィールド一覧を取得"""
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
        
        result = schema_fields.get_fields('test_schema', 'test_table', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data, [])

    @patch('dbgear_web.api.schema_fields.SchemaManager')
    @patch('dbgear_web.api.schema_fields.project')
    def test_create_field(self, mock_project, mock_schema_manager):
        """新規フィールドを追加"""
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
        
        field_request = CreateFieldRequest(
            column_name='test_field',
            display_name='Test Field',
            column_type='VARCHAR(100)',
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None
        )
        result = schema_fields.create_field('test_schema', 'test_table', self.request, field_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('added successfully', result.message)
        mock_manager.add_field.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_fields.SchemaManager')
    @patch('dbgear_web.api.schema_fields.project')
    def test_get_field(self, mock_project, mock_schema_manager):
        """特定フィールドの詳細を取得"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_field = Field(
            column_name='test_field',
            display_name='Test Field',
            column_type='INT',
            nullable=True,
            primary_key=None,
            default_value='0',
            foreign_key=None,
            comment=None
        )
        
        mock_table = MagicMock()
        mock_table.get_field.return_value = mock_field
        mock_manager.get_table.return_value = mock_table
        
        result = schema_fields.get_field('test_schema', 'test_table', 'test_field', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data.column_name, 'test_field')
        self.assertEqual(result.data.display_name, 'Test Field')
        self.assertEqual(result.data.column_type, 'INT')
        self.assertEqual(result.data.default_value, '0')

    @patch('dbgear_web.api.schema_fields.SchemaManager')
    @patch('dbgear_web.api.schema_fields.project')
    def test_get_nonexistent_field(self, mock_project, mock_schema_manager):
        """存在しないフィールドの取得でエラー"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_table = MagicMock()
        mock_table.get_field.return_value = None
        mock_manager.get_table.return_value = mock_table
        
        with self.assertRaises(Exception) as context:
            schema_fields.get_field('test_schema', 'test_table', 'nonexistent', self.request)
        self.assertIn('not found', str(context.exception))

    @patch('dbgear_web.api.schema_fields.SchemaManager')
    @patch('dbgear_web.api.schema_fields.project')
    def test_update_field(self, mock_project, mock_schema_manager):
        """フィールドを更新"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_existing_field = Field(
            column_name='test_field',
            display_name='Original Name',
            column_type='VARCHAR(50)',
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None
        )
        
        mock_table = MagicMock()
        mock_table.get_field.return_value = mock_existing_field
        mock_manager.get_table.return_value = mock_table
        
        update_request = UpdateFieldRequest(
            display_name='Updated Name',
            column_type='VARCHAR(100)'
        )
        result = schema_fields.update_field('test_schema', 'test_table', 'test_field', self.request, update_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('updated successfully', result.message)
        mock_manager.update_field.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_fields.SchemaManager')
    @patch('dbgear_web.api.schema_fields.project')
    def test_delete_field(self, mock_project, mock_schema_manager):
        """フィールドを削除"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_field = Field(
            column_name='test_field',
            display_name='Test Field',
            column_type='VARCHAR(100)',
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None
        )
        
        mock_table = MagicMock()
        mock_table.get_field.return_value = mock_field
        mock_manager.get_table.return_value = mock_table
        
        result = schema_fields.delete_field('test_schema', 'test_table', 'test_field', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertIn('deleted successfully', result.message)
        mock_manager.delete_field.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_fields.SchemaManager')
    @patch('dbgear_web.api.schema_fields.project')
    def test_field_with_foreign_key(self, mock_project, mock_schema_manager):
        """外部キー付きフィールドの作成"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        mock_table = MagicMock()
        mock_manager.get_table.return_value = mock_table
        
        field_request = CreateFieldRequest(
            column_name='user_id',
            display_name='User ID',
            column_type='INT',
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key='users.id',
            comment=None
        )
        result = schema_fields.create_field('test_schema', 'test_table', self.request, field_request)
        
        self.assertEqual(result.status, 'OK')
        mock_manager.add_field.assert_called_once()
        mock_manager.save.assert_called_once()


if __name__ == '__main__':
    unittest.main()