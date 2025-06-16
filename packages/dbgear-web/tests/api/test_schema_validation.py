import unittest
from unittest.mock import MagicMock, patch

from dbgear.core.models.project import Project
from dbgear.core.models.schema import Field, Table, Schema
from dbgear_web.api import schema_validation
from dbgear_web.api.dtos import (
    ValidateTableRequest, ValidateFieldRequest, ValidateForeignKeyRequest
)

FOLDER_PATH = '../../etc/test'


class TestSchemaValidation(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        
        self.request = MagicMock()
        self.request.app.state.project = proj

    def tearDown(self) -> None:
        pass

    @patch('dbgear_web.api.schema_validation.SchemaValidator')
    def test_validate_valid_table(self, mock_validator):
        """有効なテーブルの検証"""
        # バリデーターのモックを設定
        mock_validator.validate_table.return_value = []  # エラーなし
        
        fields = [
            Field(column_name='id', column_type='INT', primary_key=1, nullable=False, display_name='ID', default_value=None, foreign_key=None, comment=None),
            Field(column_name='name', column_type='VARCHAR(100)', primary_key=None, nullable=False, display_name='Name', default_value=None, foreign_key=None, comment=None),
            Field(column_name='email', column_type='VARCHAR(200)', primary_key=None, nullable=True, display_name='Email', default_value=None, foreign_key=None, comment=None)
        ]
        table = Table(
            instance='test_instance',
            table_name='valid_table',
            display_name='Valid Table',
            fields=fields,
            indexes=[]
        )
        
        validate_request = ValidateTableRequest(table=table)
        result = schema_validation.validate_table(self.request, validate_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('validation passed', result.message)
        mock_validator.validate_table.assert_called_once_with(table)

    @patch('dbgear_web.api.schema_validation.SchemaValidator')
    def test_validate_invalid_table_empty_name(self, mock_validator):
        """無効なテーブル（空のテーブル名）の検証"""
        # バリデーターのモックを設定
        mock_validator.validate_table.return_value = ['Table name is required']
        
        fields = [
            Field(column_name='id', column_type='INT', primary_key=1, nullable=False, display_name='ID', default_value=None, foreign_key=None, comment=None)
        ]
        table = Table(
            instance='test_instance',
            table_name='',  # 空のテーブル名
            display_name='',
            fields=fields,
            indexes=[]
        )
        
        validate_request = ValidateTableRequest(table=table)
        result = schema_validation.validate_table(self.request, validate_request)
        
        self.assertEqual(result.status, 'VALIDATION_ERROR')
        self.assertIn('validation failed', result.message)
        self.assertIsNotNone(result.data['errors'])

    @patch('dbgear_web.api.schema_validation.SchemaValidator')
    def test_validate_valid_field(self, mock_validator):
        """有効なフィールドの検証"""
        # バリデーターのモックを設定
        mock_validator.validate_field.return_value = []  # エラーなし
        
        field = Field(
            column_name='valid_field',
            display_name='Valid Field',
            column_type='VARCHAR(100)',
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None
        )
        
        validate_request = ValidateFieldRequest(field=field)
        result = schema_validation.validate_field(self.request, validate_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('validation passed', result.message)
        mock_validator.validate_field.assert_called_once_with(field)

    @patch('dbgear_web.api.schema_validation.SchemaValidator')
    def test_validate_invalid_field_empty_name(self, mock_validator):
        """無効なフィールド（空のカラム名）の検証"""
        # バリデーターのモックを設定
        mock_validator.validate_field.return_value = ['Column name is required']
        
        field = Field(
            column_name='',  # 空のカラム名
            display_name='',
            column_type='VARCHAR(100)',
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None
        )
        
        validate_request = ValidateFieldRequest(field=field)
        result = schema_validation.validate_field(self.request, validate_request)
        
        self.assertEqual(result.status, 'VALIDATION_ERROR')
        self.assertIn('validation failed', result.message)
        self.assertIsNotNone(result.data['errors'])

    @patch('dbgear_web.api.schema_validation.SchemaValidator')
    def test_validate_valid_foreign_key(self, mock_validator):
        """有効な外部キーの検証"""
        # バリデーターのモックを設定
        mock_validator.validate_foreign_key.return_value = []  # エラーなし
        
        # 参照先テーブルが存在するスキーマを作成
        schema = Schema('test_schema')
        users_table = Table(
            instance='test_instance',
            table_name='users',
            display_name='Users',
            fields=[Field(column_name='id', column_type='INT', primary_key=1, display_name='ID', nullable=False, default_value=None, foreign_key=None, comment=None)],
            indexes=[]
        )
        schema.add_table(users_table)
        
        # 外部キーフィールド
        field = Field(
            column_name='user_id',
            display_name='User ID',
            column_type='INT',
            foreign_key='users.id',
            nullable=False,
            primary_key=None,
            default_value=None,
            comment=None
        )
        
        validate_request = ValidateForeignKeyRequest(
            field=field,
            schemas={'test_schema': schema}
        )
        result = schema_validation.validate_foreign_key(self.request, validate_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('validation passed', result.message)
        mock_validator.validate_foreign_key.assert_called_once_with(field, {'test_schema': schema})

    @patch('dbgear_web.api.schema_validation.SchemaValidator')
    def test_validate_invalid_foreign_key(self, mock_validator):
        """無効な外部キー（存在しないテーブル参照）の検証"""
        # バリデーターのモックを設定
        mock_validator.validate_foreign_key.return_value = ['Referenced table not found']
        
        schema = Schema('test_schema')
        
        # 存在しないテーブルを参照する外部キーフィールド
        field = Field(
            column_name='user_id',
            display_name='User ID',
            column_type='INT',
            foreign_key='nonexistent_table.id',
            nullable=False,
            primary_key=None,
            default_value=None,
            comment=None
        )
        
        validate_request = ValidateForeignKeyRequest(
            field=field,
            schemas={'test_schema': schema}
        )
        result = schema_validation.validate_foreign_key(self.request, validate_request)
        
        self.assertEqual(result.status, 'VALIDATION_ERROR')
        self.assertIn('validation failed', result.message)
        self.assertIsNotNone(result.data['errors'])

    @patch('dbgear_web.api.schema_validation.SchemaValidator')
    @patch('dbgear_web.api.schema_validation.SchemaManager')
    @patch('dbgear_web.api.schema_validation.project')
    def test_validate_schema_valid(self, mock_project, mock_schema_manager, mock_validator):
        """有効なスキーマ全体の検証"""
        # プロジェクトとSchemaManagerのモックを設定
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_schema = Schema('test_schema')
        mock_manager.get_schema.return_value = mock_schema
        
        # バリデーターのモックを設定（エラーなし）
        mock_validator.validate_table.return_value = []
        mock_validator.validate_field.return_value = []
        mock_validator.validate_foreign_key.return_value = []
        
        result = schema_validation.validate_schema('test_schema', self.request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('validation passed', result.message)

    @patch('dbgear_web.api.schema_validation.SchemaManager')
    @patch('dbgear_web.api.schema_validation.project')
    def test_validate_schema_nonexistent(self, mock_project, mock_schema_manager):
        """存在しないスキーマの検証でエラー"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = False
        
        with self.assertRaises(Exception) as context:
            schema_validation.validate_schema('nonexistent', self.request)
        self.assertIn('not found', str(context.exception))


if __name__ == '__main__':
    unittest.main()