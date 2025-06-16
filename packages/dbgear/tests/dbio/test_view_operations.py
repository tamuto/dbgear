import unittest
from unittest.mock import Mock, patch

from dbgear.core.dbio import view
from dbgear.core.models.schema import View


class TestViewOperations(unittest.TestCase):

    def setUp(self):
        self.mock_conn = Mock()
        self.test_view = View(
            instance='test_db',
            view_name='test_view',
            display_name='テストビュー',
            select_statement='SELECT id, name FROM users WHERE active = 1',
            comment='アクティブなユーザーのみを表示するビュー'
        )

    @patch('dbgear.core.dbio.view.engine')
    def test_is_exist_true(self, mock_engine):
        """Test view existence check when view exists."""
        mock_engine.select_one.return_value = {'TABLE_NAME': 'test_view'}
        
        result = view.is_exist(self.mock_conn, 'test_db', self.test_view)
        
        self.assertTrue(result)
        mock_engine.select_one.assert_called_once_with(
            self.mock_conn,
            '''
        SELECT TABLE_NAME FROM information_schema.views
        WHERE table_schema = :env and table_name = :view_name
        ''',
            {'env': 'test_db', 'view_name': 'test_view'}
        )

    @patch('dbgear.core.dbio.view.engine')
    def test_is_exist_false(self, mock_engine):
        """Test view existence check when view doesn't exist."""
        mock_engine.select_one.return_value = None
        
        result = view.is_exist(self.mock_conn, 'test_db', self.test_view)
        
        self.assertFalse(result)

    @patch('dbgear.core.dbio.view.engine')
    def test_drop(self, mock_engine):
        """Test view drop functionality."""
        view.drop(self.mock_conn, 'test_db', self.test_view)
        
        mock_engine.execute.assert_called_once_with(
            self.mock_conn,
            'DROP VIEW IF EXISTS test_db.test_view'
        )

    @patch('dbgear.core.dbio.view.engine')
    def test_create(self, mock_engine):
        """Test view creation functionality."""
        view.create(self.mock_conn, 'test_db', self.test_view)
        
        expected_sql = 'CREATE VIEW test_db.test_view AS SELECT id, name FROM users WHERE active = 1'
        mock_engine.execute.assert_called_once_with(
            self.mock_conn,
            expected_sql
        )

    @patch('dbgear.core.dbio.view.engine')
    def test_create_or_replace(self, mock_engine):
        """Test view create or replace functionality."""
        view.create_or_replace(self.mock_conn, 'test_db', self.test_view)
        
        expected_sql = 'CREATE OR REPLACE VIEW test_db.test_view AS SELECT id, name FROM users WHERE active = 1'
        mock_engine.execute.assert_called_once_with(
            self.mock_conn,
            expected_sql
        )

    @patch('dbgear.core.dbio.view.engine')
    def test_get_view_definition_exists(self, mock_engine):
        """Test getting view definition when view exists."""
        mock_engine.select_one.return_value = {
            'VIEW_DEFINITION': 'SELECT id, name FROM users WHERE active = 1'
        }
        
        result = view.get_view_definition(self.mock_conn, 'test_db', 'test_view')
        
        self.assertEqual(result, 'SELECT id, name FROM users WHERE active = 1')
        mock_engine.select_one.assert_called_once_with(
            self.mock_conn,
            '''
        SELECT VIEW_DEFINITION FROM information_schema.views
        WHERE table_schema = :env and table_name = :view_name
        ''',
            {'env': 'test_db', 'view_name': 'test_view'}
        )

    @patch('dbgear.core.dbio.view.engine')
    def test_get_view_definition_not_exists(self, mock_engine):
        """Test getting view definition when view doesn't exist."""
        mock_engine.select_one.return_value = None
        
        result = view.get_view_definition(self.mock_conn, 'test_db', 'test_view')
        
        self.assertIsNone(result)

    @patch('dbgear.core.dbio.view.engine')
    def test_validate_dependencies_all_exist(self, mock_engine):
        """Test dependency validation when all dependencies exist."""
        # Mock view with dependencies
        test_view_with_deps = View(
            instance='test_db',
            view_name='complex_view',
            display_name='複雑なビュー',
            select_statement='SELECT u.id, p.title FROM users u JOIN posts p ON u.id = p.user_id'
        )
        test_view_with_deps._dependencies = ['users', 'posts']
        
        # Mock that both tables exist
        mock_engine.select_one.side_effect = [
            {'TABLE_NAME': 'users'},  # users table exists
            None,  # users view doesn't exist
            {'TABLE_NAME': 'posts'},  # posts table exists
            None   # posts view doesn't exist
        ]
        
        # Should not raise an exception
        view.validate_dependencies(self.mock_conn, 'test_db', test_view_with_deps)
        
        # Verify all dependency checks were made
        self.assertEqual(mock_engine.select_one.call_count, 4)

    @patch('dbgear.core.dbio.view.engine')
    def test_validate_dependencies_missing(self, mock_engine):
        """Test dependency validation when some dependencies are missing."""
        # Mock view with dependencies
        test_view_with_deps = View(
            instance='test_db',
            view_name='complex_view',
            display_name='複雑なビュー',
            select_statement='SELECT u.id, p.title FROM users u JOIN posts p ON u.id = p.user_id'
        )
        test_view_with_deps._dependencies = ['users', 'missing_table']
        
        # Mock that users exists but missing_table doesn't
        mock_engine.select_one.side_effect = [
            {'TABLE_NAME': 'users'},  # users table exists
            None,  # users view doesn't exist
            None,  # missing_table table doesn't exist
            None   # missing_table view doesn't exist
        ]
        
        with self.assertRaises(ValueError) as context:
            view.validate_dependencies(self.mock_conn, 'test_db', test_view_with_deps)
        
        self.assertIn("Dependency 'missing_table' not found", str(context.exception))

    @patch('dbgear.core.dbio.view.engine')
    def test_validate_dependencies_with_view_dependency(self, mock_engine):
        """Test dependency validation when dependency is a view."""
        # Mock view with dependencies
        test_view_with_deps = View(
            instance='test_db',
            view_name='complex_view',
            display_name='複雑なビュー',
            select_statement='SELECT * FROM user_summary'
        )
        test_view_with_deps._dependencies = ['user_summary']
        
        # Mock that user_summary is a view (not a table)
        mock_engine.select_one.side_effect = [
            None,  # user_summary table doesn't exist
            {'TABLE_NAME': 'user_summary'}  # user_summary view exists
        ]
        
        # Should not raise an exception
        view.validate_dependencies(self.mock_conn, 'test_db', test_view_with_deps)

    def test_view_sql_formatting(self):
        """Test that SQL statements are properly formatted in view operations."""
        multiline_view = View(
            instance='test_db',
            view_name='multiline_view',
            display_name='複数行ビュー',
            select_statement='''
                SELECT 
                    u.id,
                    u.name,
                    COUNT(p.id) as post_count
                FROM users u
                LEFT JOIN posts p ON u.id = p.user_id
                GROUP BY u.id, u.name
            '''
        )
        
        with patch('dbgear.core.dbio.view.engine') as mock_engine:
            view.create(self.mock_conn, 'test_db', multiline_view)
            
            # Verify the SQL includes the full multiline statement
            call_args = mock_engine.execute.call_args[0]
            executed_sql = call_args[1]
            
            self.assertIn('CREATE VIEW test_db.multiline_view AS', executed_sql)
            self.assertIn('SELECT', executed_sql)
            self.assertIn('FROM users u', executed_sql)
            self.assertIn('LEFT JOIN posts p', executed_sql)
            self.assertIn('GROUP BY', executed_sql)


if __name__ == '__main__':
    unittest.main()