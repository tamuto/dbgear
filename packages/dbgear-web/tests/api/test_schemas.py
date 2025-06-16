import unittest
from unittest.mock import MagicMock, patch

from dbgear.core.models.project import Project
from dbgear_web.api import schemas
from dbgear_web.api.dtos import CreateSchemaRequest

FOLDER_PATH = '../../etc/test'


class TestSchemas(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        
        self.request = MagicMock()
        self.request.app.state.project = proj

    def tearDown(self) -> None:
        pass

    @patch('dbgear_web.api.schemas.SchemaManager')
    @patch('dbgear_web.api.schemas.project')
    def test_get_schemas_empty(self, mock_project, mock_schema_manager):
        """空の状態でスキーマ一覧を取得"""
        # projectとSchemaManagerのモックを設定
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.get_schemas.return_value = {}
        
        result = schemas.get_schemas(self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data, [])

    @patch('dbgear_web.api.schemas.SchemaManager')
    @patch('dbgear_web.api.schemas.project')
    def test_create_schema(self, mock_project, mock_schema_manager):
        """新規スキーマを作成"""
        # projectとSchemaManagerのモックを設定
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = False
        
        schema_request = CreateSchemaRequest(schema_name='test_schema')
        result = schemas.create_schema(self.request, schema_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('created successfully', result.message)
        mock_manager.create_schema.assert_called_once_with('test_schema')
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schemas.SchemaManager')
    @patch('dbgear_web.api.schemas.project')
    def test_reload_schemas(self, mock_project, mock_schema_manager):
        """スキーマファイルの再読み込み"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        
        result = schemas.reload_schemas(self.request)
        self.assertEqual(result.status, 'OK')
        self.assertIn('reloaded successfully', result.message)
        mock_manager.reload.assert_called_once()

    @patch('dbgear_web.api.schemas.SchemaManager')
    @patch('dbgear_web.api.schemas.project')
    def test_save_schemas(self, mock_project, mock_schema_manager):
        """スキーマファイルの保存"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        
        result = schemas.save_schemas(self.request)
        self.assertEqual(result.status, 'OK')
        self.assertIn('saved successfully', result.message)
        mock_manager.save.assert_called_once()


if __name__ == '__main__':
    unittest.main()