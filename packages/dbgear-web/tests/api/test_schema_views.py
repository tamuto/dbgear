import unittest
from unittest.mock import MagicMock, patch

from dbgear.core.models.project import Project
from dbgear.core.models.schema import Schema, View
from dbgear_web.api import schema_views
from dbgear_web.api.dtos import CreateViewRequest, UpdateViewRequest

FOLDER_PATH = '../../etc/test'


class TestSchemaViews(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        
        self.request = MagicMock()
        self.request.app.state.project = proj

    def tearDown(self) -> None:
        pass

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_get_views_empty(self, mock_project, mock_schema_manager):
        """空のスキーマでビュー一覧を取得"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_schema = Schema('test_schema')
        mock_manager.get_schema.return_value = mock_schema
        
        result = schema_views.get_views('test_schema', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data, [])

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_create_view(self, mock_project, mock_schema_manager):
        """新規ビューを作成"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_schema = MagicMock()
        mock_schema.views = {}
        mock_manager.get_schema.return_value = mock_schema
        
        view_request = CreateViewRequest(
            instance='test_instance',
            view_name='test_view',
            display_name='Test View',
            select_statement='SELECT * FROM test_table',
            comment='This is a test view'
        )
        result = schema_views.create_view('test_schema', self.request, view_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('created successfully', result.message)
        mock_schema.add_view.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_create_duplicate_view(self, mock_project, mock_schema_manager):
        """重複ビュー作成でエラー"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_schema = MagicMock()
        mock_schema.views = {'test_view': MagicMock()}  # 既存ビュー
        mock_manager.get_schema.return_value = mock_schema
        
        view_request = CreateViewRequest(
            instance='test_instance',
            view_name='test_view',
            select_statement='SELECT * FROM test_table'
        )
        
        with self.assertRaises(Exception) as context:
            schema_views.create_view('test_schema', self.request, view_request)
        self.assertIn('already exists', str(context.exception))

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_get_view(self, mock_project, mock_schema_manager):
        """特定ビューの詳細を取得"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_view = View(
            instance='test_instance',
            view_name='test_view',
            display_name='Test View',
            select_statement='SELECT id, name FROM test_table WHERE active = 1',
            comment='Active records only'
        )
        
        mock_schema = MagicMock()
        mock_schema.views = {'test_view': mock_view}
        mock_manager.get_schema.return_value = mock_schema
        
        result = schema_views.get_view('test_schema', 'test_view', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertEqual(result.data.view_name, 'test_view')
        self.assertEqual(result.data.display_name, 'Test View')
        self.assertEqual(result.data.select_statement, 'SELECT id, name FROM test_table WHERE active = 1')
        self.assertEqual(result.data.comment, 'Active records only')

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_get_nonexistent_view(self, mock_project, mock_schema_manager):
        """存在しないビューの取得でエラー"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_schema = MagicMock()
        mock_schema.views = {}  # 空のビュー辞書
        mock_manager.get_schema.return_value = mock_schema
        
        with self.assertRaises(Exception) as context:
            schema_views.get_view('test_schema', 'nonexistent', self.request)
        self.assertIn('not found', str(context.exception))

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_update_view(self, mock_project, mock_schema_manager):
        """ビューを更新"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_existing_view = View(
            instance='test_instance',
            view_name='test_view',
            display_name='Original View',
            select_statement='SELECT * FROM test_table',
            comment='Original comment'
        )
        
        mock_schema = MagicMock()
        mock_schema.views = {'test_view': mock_existing_view}
        mock_manager.get_schema.return_value = mock_schema
        
        update_request = UpdateViewRequest(
            display_name='Updated View',
            select_statement='SELECT id, name FROM test_table WHERE status = "active"',
            comment='Updated comment'
        )
        result = schema_views.update_view('test_schema', 'test_view', self.request, update_request)
        
        self.assertEqual(result.status, 'OK')
        self.assertIn('updated successfully', result.message)
        mock_schema.update_view.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_delete_view(self, mock_project, mock_schema_manager):
        """ビューを削除"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_view = View(
            instance='test_instance',
            view_name='test_view',
            display_name='Test View',
            select_statement='SELECT * FROM test_table',
            comment=None
        )
        
        mock_schema = MagicMock()
        mock_schema.views = {'test_view': mock_view}
        mock_manager.get_schema.return_value = mock_schema
        
        result = schema_views.delete_view('test_schema', 'test_view', self.request)
        self.assertEqual(result.status, 'OK')
        self.assertIn('deleted successfully', result.message)
        mock_schema.delete_view.assert_called_once()
        mock_manager.save.assert_called_once()

    @patch('dbgear_web.api.schema_views.SchemaManager')
    @patch('dbgear_web.api.schema_views.project')
    def test_complex_view_sql(self, mock_project, mock_schema_manager):
        """複雑なSQL文を持つビューの作成"""
        mock_proj = MagicMock()
        mock_proj.definition_file.return_value = '/tmp/test_schema.yaml'
        mock_project.return_value = mock_proj
        
        mock_manager = mock_schema_manager.return_value
        mock_manager.schema_exists.return_value = True
        
        mock_schema = MagicMock()
        mock_schema.views = {}
        mock_manager.get_schema.return_value = mock_schema
        
        complex_sql = """
        SELECT 
            u.id,
            u.name,
            u.email,
            COUNT(o.id) as order_count,
            SUM(o.total) as total_amount
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.active = 1
        GROUP BY u.id, u.name, u.email
        HAVING COUNT(o.id) > 0
        ORDER BY total_amount DESC
        """
        
        view_request = CreateViewRequest(
            instance='test_instance',
            view_name='user_order_summary',
            display_name='User Order Summary',
            select_statement=complex_sql.strip(),
            comment='Summary of user orders with totals'
        )
        result = schema_views.create_view('test_schema', self.request, view_request)
        
        self.assertEqual(result.status, 'OK')
        mock_schema.add_view.assert_called_once()
        mock_manager.save.assert_called_once()


if __name__ == '__main__':
    unittest.main()