import tempfile
import unittest
import os

from dbgear.core.models.fileio import save_yaml
from dbgear.core.definitions.dbgear_schema import retrieve
from dbgear.core.models.schema import Schema, View


class TestDBGearSchemaViews(unittest.TestCase):

    def setUp(self):
        self.test_schema_data = {
            'schemas': {
                'main': {
                    'tables': {
                        'users': {
                            'display_name': 'ユーザー',
                            'fields': [
                                {
                                    'column_name': 'id',
                                    'display_name': 'ID',
                                    'column_type': 'BIGINT',
                                    'nullable': False,
                                    'primary_key': 1
                                },
                                {
                                    'column_name': 'name',
                                    'display_name': '名前',
                                    'column_type': 'VARCHAR(100)',
                                    'nullable': False
                                },
                                {
                                    'column_name': 'email',
                                    'display_name': 'メールアドレス',
                                    'column_type': 'VARCHAR(255)',
                                    'nullable': True
                                }
                            ]
                        },
                        'orders': {
                            'display_name': '注文',
                            'fields': [
                                {
                                    'column_name': 'id',
                                    'column_type': 'BIGINT',
                                    'nullable': False,
                                    'primary_key': 1
                                },
                                {
                                    'column_name': 'user_id',
                                    'column_type': 'BIGINT',
                                    'nullable': False,
                                    'foreign_key': 'users.id'
                                },
                                {
                                    'column_name': 'total_amount',
                                    'column_type': 'DECIMAL(10,2)',
                                    'nullable': False
                                }
                            ]
                        }
                    },
                    'views': {
                        'user_summary': {
                            'display_name': 'ユーザー集計ビュー',
                            'select_statement': '''
                                SELECT 
                                    u.id,
                                    u.name,
                                    u.email,
                                    COUNT(o.id) as order_count,
                                    COALESCE(SUM(o.total_amount), 0) as total_spent
                                FROM users u
                                LEFT JOIN orders o ON u.id = o.user_id
                                GROUP BY u.id, u.name, u.email
                            ''',
                            'comment': 'ユーザーごとの注文集計情報を表示'
                        },
                        'active_users': {
                            'display_name': 'アクティブユーザー',
                            'select_statement': '''
                                SELECT 
                                    u.id,
                                    u.name,
                                    u.email
                                FROM users u
                                WHERE u.email IS NOT NULL
                            '''
                        }
                    }
                }
            }
        }

    def test_basic_view_parsing(self):
        """Test basic view parsing functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            
            self.assertIn('main', schemas)
            main_schema = schemas['main']
            
            views = main_schema.get_views()
            self.assertEqual(len(views), 2)
            self.assertIn('user_summary', views)
            self.assertIn('active_users', views)

    def test_view_properties(self):
        """Test view properties parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            user_summary_view = schemas['main'].get_view('user_summary')
            
            self.assertEqual(user_summary_view.view_name, 'user_summary')
            self.assertEqual(user_summary_view.display_name, 'ユーザー集計ビュー')
            self.assertEqual(user_summary_view.instance, 'main')
            self.assertEqual(user_summary_view.comment, 'ユーザーごとの注文集計情報を表示')
            self.assertIn('SELECT', user_summary_view.select_statement)
            self.assertIn('users u', user_summary_view.select_statement)

    def test_view_without_comment(self):
        """Test view parsing without comment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            active_users_view = schemas['main'].get_view('active_users')
            
            self.assertEqual(active_users_view.view_name, 'active_users')
            self.assertEqual(active_users_view.display_name, 'アクティブユーザー')
            self.assertIsNone(active_users_view.comment)

    def test_view_crud_operations(self):
        """Test view CRUD operations in schema."""
        schema = Schema('test')
        
        # Create a test view
        test_view = View(
            instance='test',
            view_name='test_view',
            display_name='テストビュー',
            select_statement='SELECT * FROM test_table',
            comment='テスト用のビュー'
        )
        
        # Add view
        schema.add_view(test_view)
        self.assertTrue(schema.view_exists('test_view'))
        self.assertEqual(len(schema.get_views()), 1)
        
        # Get view
        retrieved_view = schema.get_view('test_view')
        self.assertEqual(retrieved_view.view_name, 'test_view')
        self.assertEqual(retrieved_view.display_name, 'テストビュー')
        
        # Update view
        updated_view = View(
            instance='test',
            view_name='test_view',
            display_name='更新されたテストビュー',
            select_statement='SELECT id, name FROM test_table',
            comment='更新されたテスト用のビュー'
        )
        schema.update_view('test_view', updated_view)
        
        retrieved_view = schema.get_view('test_view')
        self.assertEqual(retrieved_view.display_name, '更新されたテストビュー')
        self.assertEqual(retrieved_view.comment, '更新されたテスト用のビュー')
        
        # Remove view
        schema.remove_view('test_view')
        self.assertFalse(schema.view_exists('test_view'))
        self.assertEqual(len(schema.get_views()), 0)

    def test_view_not_found_errors(self):
        """Test error handling for non-existent views."""
        schema = Schema('test')
        
        with self.assertRaises(KeyError):
            schema.get_view('non_existent')
        
        with self.assertRaises(KeyError):
            schema.update_view('non_existent', View(
                instance='test',
                view_name='test',
                display_name='test',
                select_statement='SELECT 1'
            ))
        
        with self.assertRaises(KeyError):
            schema.remove_view('non_existent')

    def test_schema_with_tables_and_views(self):
        """Test schema containing both tables and views."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            main_schema = schemas['main']
            
            # Verify both tables and views exist
            tables = main_schema.get_tables()
            views = main_schema.get_views()
            
            self.assertEqual(len(tables), 2)
            self.assertEqual(len(views), 2)
            
            self.assertIn('users', tables)
            self.assertIn('orders', tables)
            self.assertIn('user_summary', views)
            self.assertIn('active_users', views)

    def test_mapping_support_for_views(self):
        """Test schema name mapping for views."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            mapping = {'main': 'production'}
            schemas = retrieve(tmpdir, 'schema.yaml', mapping)
            
            self.assertIn('production', schemas)
            prod_schema = schemas['production']
            
            # Views should have correct instance name after mapping
            user_summary_view = prod_schema.get_view('user_summary')
            self.assertEqual(user_summary_view.instance, 'production')

    def test_minimal_view_definition(self):
        """Test minimal view definition with only required fields."""
        minimal_schema = {
            'schemas': {
                'test': {
                    'views': {
                        'simple_view': {
                            'select_statement': 'SELECT 1 as one'
                        }
                    }
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, minimal_schema)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            simple_view = schemas['test'].get_view('simple_view')
            
            self.assertEqual(simple_view.view_name, 'simple_view')
            self.assertEqual(simple_view.display_name, 'simple_view')  # Defaults to view_name
            self.assertEqual(simple_view.select_statement, 'SELECT 1 as one')
            self.assertIsNone(simple_view.comment)


if __name__ == '__main__':
    unittest.main()