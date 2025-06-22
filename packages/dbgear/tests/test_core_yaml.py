import unittest
import tempfile
import os
import yaml

from dbgear.core.models.project import Project
from dbgear.core.models.schema import SchemaManager


class TestCoreYamlOperations(unittest.TestCase):
    """Test core YAML operations for Project and SchemaManager"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        # self.temp_dir = '.'
        self.project_yaml_path = os.path.join(self.temp_dir, 'project.yaml')
        self.schema_yaml_path = os.path.join(self.temp_dir, 'schema.yaml')

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_comprehensive_test_data(self):
        """Create comprehensive project and schema test data"""
        # Create project.yaml data
        project_data = {
            'project_name': 'Comprehensive Test Project',
            'description': 'Full feature test with complex schema',
        }

        # Create comprehensive schema.yaml data
        schema_data = {
            'schemas': {
                'main': {
                    'tables': {
                        'users': {
                            'display_name': 'ユーザー',
                            'columns': [
                                {
                                    'column_name': 'id',
                                    'display_name': 'ID',
                                    'column_type': {
                                        'column_type': 'BIGINT',
                                        'base_type': 'BIGINT'
                                    },
                                    'nullable': False,
                                    'primary_key': 1,
                                    'auto_increment': True
                                },
                                {
                                    'column_name': 'name',
                                    'display_name': '名前',
                                    'column_type': {
                                        'column_type': 'VARCHAR(100)',
                                        'base_type': 'VARCHAR',
                                        'length': 100
                                    },
                                    'nullable': False,
                                    'charset': 'utf8mb4',
                                    'collation': 'utf8mb4_unicode_ci'
                                },
                                {
                                    'column_name': 'price',
                                    'display_name': '価格',
                                    'column_type': {
                                        'column_type': 'DECIMAL(10,2)',
                                        'base_type': 'DECIMAL',
                                        'precision': 10,
                                        'scale': 2
                                    },
                                    'nullable': False,
                                    'default_value': '0.00'
                                },
                                {
                                    'column_name': 'status',
                                    'display_name': 'ステータス',
                                    'column_type': {
                                        'column_type': "ENUM('active','inactive')",
                                        'base_type': 'ENUM',
                                        'items': ['active', 'inactive']
                                    },
                                    'nullable': False,
                                    'default_value': 'active'
                                }
                            ],
                            'indexes': [
                                {
                                    'index_name': 'idx_name_unique',
                                    'columns': ['name'],
                                    'unique': True,
                                    'index_type': 'BTREE'
                                },
                                {
                                    'index_name': 'idx_price_status',
                                    'columns': ['price', 'status'],
                                    'unique': False,
                                    'index_type': 'BTREE'
                                }
                            ],
                            'relations': [
                                {
                                    'target': {
                                        'schema': 'main',
                                        'table_name': 'departments'
                                    },
                                    'bind_columns': [
                                        {
                                            'source_column': 'department_id',
                                            'target_column': 'id'
                                        }
                                    ],
                                    'constraint_name': 'fk_user_department',
                                    'on_delete': 'CASCADE',
                                    'on_update': 'RESTRICT',
                                    'relationship_type': 'association'
                                }
                            ],
                            'mysql_options': {
                                'engine': 'InnoDB',
                                'charset': 'utf8mb4',
                                'collation': 'utf8mb4_unicode_ci',
                                'partition_by': 'HASH',
                                'partition_expression': 'id',
                                'partition_count': 4,
                                'row_format': 'DYNAMIC'
                            },
                            'notes': [
                                {
                                    'title': '設計メモ',
                                    'content': 'ユーザーマスターテーブル - パーティション化済み',
                                    'checked': True
                                }
                            ]
                        }
                    },
                    'views': {
                        'active_users': {
                            'display_name': 'アクティブユーザー',
                            'select_statement': "SELECT id, name, price FROM users WHERE status = 'active'",
                            'notes': [
                                {
                                    'title': 'ビューの目的',
                                    'content': 'アクティブなユーザーのみを表示するビュー',
                                    'checked': False
                                }
                            ]
                        }
                    }
                }
            }
        }

        return project_data, schema_data

    def write_test_files(self, project_data, schema_data):
        """Write test data to YAML files"""
        with open(self.project_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(project_data, f, allow_unicode=True)

        with open(self.schema_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(schema_data, f, allow_unicode=True)

    def test_comprehensive_yaml_roundtrip(self):
        """Test comprehensive YAML file read/write operations"""
        project_data, schema_data = self.create_comprehensive_test_data()
        self.write_test_files(project_data, schema_data)

        # === PROJECT LOADING TEST ===
        project = Project.load(self.temp_dir)

        # Verify project data
        self.assertEqual(project.project_name, 'Comprehensive Test Project')
        self.assertEqual(project.description, 'Full feature test with complex schema')

        # === SCHEMA STRUCTURE VERIFICATION ===
        self.assertIsInstance(project.schemas, SchemaManager)
        main_schema = project.schemas['main']
        users_table = main_schema.tables['users']

        # Test table structure
        self.assertEqual(users_table.display_name, 'ユーザー')
        self.assertEqual(len(users_table.columns), 4)
        self.assertEqual(len(users_table.indexes), 2)
        self.assertEqual(len(users_table.relations), 1)
        self.assertEqual(len(users_table.notes), 1)

        # Test column types (all different types)
        id_column = users_table.columns['id']
        self.assertEqual(id_column.column_type.base_type, 'BIGINT')
        self.assertTrue(id_column.auto_increment)

        name_column = users_table.columns['name']
        self.assertEqual(name_column.column_type.base_type, 'VARCHAR')
        self.assertEqual(name_column.column_type.length, 100)
        self.assertEqual(name_column.charset, 'utf8mb4')

        price_column = users_table.columns['price']
        self.assertEqual(price_column.column_type.base_type, 'DECIMAL')
        self.assertEqual(price_column.column_type.precision, 10)
        self.assertEqual(price_column.column_type.scale, 2)

        status_column = users_table.columns['status']
        self.assertEqual(status_column.column_type.base_type, 'ENUM')
        self.assertEqual(status_column.column_type.items, ['active', 'inactive'])

        # Test indexes
        unique_index = next(idx for idx in users_table.indexes if idx.unique)
        self.assertEqual(unique_index.index_name, 'idx_name_unique')
        self.assertTrue(unique_index.unique)

        # Test relations
        relation = users_table.relations[0]
        self.assertEqual(relation.target.table_name, 'departments')
        self.assertEqual(relation.constraint_name, 'fk_user_department')
        self.assertEqual(relation.on_delete, 'CASCADE')

        # Test MySQL options
        mysql_opts = users_table.mysql_options
        self.assertEqual(mysql_opts.engine, 'InnoDB')
        self.assertEqual(mysql_opts.partition_by, 'HASH')
        self.assertEqual(mysql_opts.partition_count, 4)

        # Test notes
        note = users_table.notes[0]
        self.assertEqual(note.title, '設計メモ')
        self.assertTrue(note.checked)

        # Test view
        active_users_view = main_schema.views['active_users']
        self.assertEqual(active_users_view.display_name, 'アクティブユーザー')
        self.assertIn("status = 'active'", active_users_view.select_statement)
        self.assertEqual(len(active_users_view.notes), 1)

        # === SCHEMA SAVE/LOAD ROUNDTRIP TEST ===
        # Save the loaded schema back to file
        roundtrip_schema_path = os.path.join(self.temp_dir, 'roundtrip_schema.yaml')
        project.schemas.save(roundtrip_schema_path)

        # Load it back
        reloaded_schema_manager = SchemaManager.load(roundtrip_schema_path)

        # Verify it matches exactly
        reloaded_table = reloaded_schema_manager['main'].tables['users']
        self.assertEqual(reloaded_table.display_name, users_table.display_name)
        self.assertEqual(len(reloaded_table.columns), len(users_table.columns))
        self.assertEqual(len(reloaded_table.indexes), len(users_table.indexes))
        self.assertEqual(len(reloaded_table.relations), len(users_table.relations))

        # Verify complex column type preservation
        reloaded_price = reloaded_table.columns['price']
        self.assertEqual(reloaded_price.column_type.precision, 10)
        self.assertEqual(reloaded_price.column_type.scale, 2)


if __name__ == '__main__':
    unittest.main()
