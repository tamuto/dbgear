import tempfile
import unittest
import os

from dbgear.core.models.fileio import save_yaml
from dbgear.core.definitions.dbgear_schema import retrieve
from dbgear.core.models.schema import Schema, Table, Field, Index


class TestDBGearSchema(unittest.TestCase):

    def setUp(self):
        self.test_schema_data = {
            'schemas': {
                'main': {
                    'tables': {
                        'users': {
                            'display_name': 'ユーザー',
                            'comment': 'システムユーザー情報',
                            'fields': [
                                {
                                    'column_name': 'id',
                                    'display_name': 'ID',
                                    'column_type': 'BIGINT',
                                    'nullable': False,
                                    'primary_key': 1,
                                    'comment': 'プライマリキー'
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
                            ],
                            'indexes': [
                                {
                                    'index_name': 'idx_email',
                                    'columns': ['email']
                                }
                            ]
                        },
                        'posts': {
                            'display_name': '投稿',
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
                                    'column_name': 'title',
                                    'column_type': 'VARCHAR(200)',
                                    'nullable': False
                                }
                            ]
                        }
                    }
                }
            }
        }

    def test_basic_schema_parsing(self):
        """Test basic schema parsing functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            
            self.assertIn('main', schemas)
            self.assertIsInstance(schemas['main'], Schema)
            
            main_schema = schemas['main']
            self.assertEqual(main_schema.name, 'main')
            
            tables = main_schema.get_tables()
            self.assertIn('users', tables)
            self.assertIn('posts', tables)

    def test_field_parsing(self):
        """Test field parsing with various attributes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            users_table = schemas['main'].get_table('users')
            
            self.assertEqual(len(users_table.fields), 3)
            
            id_field = users_table.fields[0]
            self.assertEqual(id_field.column_name, 'id')
            self.assertEqual(id_field.display_name, 'ID')
            self.assertEqual(id_field.column_type, 'BIGINT')
            self.assertEqual(id_field.nullable, False)
            self.assertEqual(id_field.primary_key, 1)
            self.assertEqual(id_field.comment, 'プライマリキー')
            
            email_field = users_table.fields[2]
            self.assertEqual(email_field.column_name, 'email')
            self.assertEqual(email_field.nullable, True)

    def test_index_parsing(self):
        """Test index parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            users_table = schemas['main'].get_table('users')
            
            self.assertEqual(len(users_table.indexes), 1)
            
            email_index = users_table.indexes[0]
            self.assertEqual(email_index.index_name, 'idx_email')
            self.assertEqual(email_index.columns, ['email'])

    def test_foreign_key_parsing(self):
        """Test foreign key parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            posts_table = schemas['main'].get_table('posts')
            
            user_id_field = posts_table.fields[1]
            self.assertEqual(user_id_field.column_name, 'user_id')
            self.assertEqual(user_id_field.foreign_key, 'users.id')

    def test_mapping_support(self):
        """Test schema name mapping."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, self.test_schema_data)
            
            mapping = {'main': 'production'}
            schemas = retrieve(tmpdir, 'schema.yaml', mapping)
            
            self.assertIn('production', schemas)
            self.assertNotIn('main', schemas)
            
            prod_schema = schemas['production']
            self.assertEqual(prod_schema.name, 'production')

    def test_minimal_field_definition(self):
        """Test minimal field definition with only required fields."""
        minimal_schema = {
            'schemas': {
                'test': {
                    'tables': {
                        'simple': {
                            'fields': [
                                {
                                    'column_name': 'id',
                                    'column_type': 'INTEGER'
                                }
                            ]
                        }
                    }
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'schema.yaml')
            save_yaml(schema_file, minimal_schema)
            
            schemas = retrieve(tmpdir, 'schema.yaml')
            simple_table = schemas['test'].get_table('simple')
            
            id_field = simple_table.fields[0]
            self.assertEqual(id_field.column_name, 'id')
            self.assertEqual(id_field.display_name, 'id')  # Defaults to column_name
            self.assertEqual(id_field.column_type, 'INTEGER')
            self.assertEqual(id_field.nullable, True)  # Default value
            self.assertIsNone(id_field.primary_key)
            self.assertIsNone(id_field.default_value)
            self.assertIsNone(id_field.foreign_key)
            self.assertIsNone(id_field.comment)

    def test_invalid_schema_file(self):
        """Test error handling for invalid schema files."""
        invalid_schema = {'invalid': 'structure'}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_file = os.path.join(tmpdir, 'invalid.yaml')
            save_yaml(schema_file, invalid_schema)
            
            with self.assertRaises(ValueError) as context:
                retrieve(tmpdir, 'invalid.yaml')
            
            self.assertIn("must contain 'schemas' key", str(context.exception))


if __name__ == '__main__':
    unittest.main()