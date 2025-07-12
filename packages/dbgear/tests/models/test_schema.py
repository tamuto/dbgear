import unittest
import tempfile
import os
import yaml

from dbgear.models.schema import SchemaManager, Schema
from dbgear.models.table import Table
from dbgear.models.column import Column
from dbgear.models.column_type import ColumnType, ColumnTypeItem


class TestSchema(unittest.TestCase):
    """Test SchemaManager YAML file I/O operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.schema_yaml_path = os.path.join(self.temp_dir, 'schema.yaml')

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_schema_manager_save_and_load(self):
        """Test SchemaManager save and load operations"""
        # Create test schema
        schema_manager = SchemaManager()

        # Add schema with table and columns
        main_schema = Schema(name='main')
        schema_manager.schemas['main'] = main_schema

        # Add table with columns
        users_table = Table(
            instance='main',
            table_name='users',
            display_name='ユーザー'
        )

        # Add columns to manager
        id_column = Column(
            column_name='id',
            display_name='ID',
            column_type=ColumnType(column_type='BIGINT', base_type='BIGINT'),
            nullable=False,
            primary_key=1
        )
        users_table.columns.append(id_column)

        name_column = Column(
            column_name='name',
            display_name='名前',
            column_type=ColumnType(column_type='VARCHAR(100)', base_type='VARCHAR', length=100),
            nullable=False
        )
        users_table.columns.append(name_column)

        main_schema.tables_['users'] = users_table

        # Test save
        schema_manager.save(self.schema_yaml_path)
        self.assertTrue(os.path.exists(self.schema_yaml_path))

        # Test load
        loaded_schema_manager = SchemaManager.load(self.schema_yaml_path)
        self.assertIn('main', loaded_schema_manager.schemas)

        loaded_schema = loaded_schema_manager['main']
        self.assertEqual(loaded_schema.name, 'main')

        loaded_table = loaded_schema.tables['users']
        self.assertEqual(loaded_table.display_name, 'ユーザー')
        self.assertEqual(len(loaded_table.columns), 2)

    def test_schema_load_from_existing_yaml(self):
        """Test loading SchemaManager from existing YAML file"""
        # Create test schema data
        schema_data = {
            'schemas': {
                'main': {
                    'tables': {
                        'products': {
                            'displayName': '商品',
                            'columns': [
                                {
                                    'columnName': 'id',
                                    'displayName': 'ID',
                                    'columnType': {
                                        'columnType': 'BIGINT',
                                        'baseType': 'BIGINT'
                                    },
                                    'nullable': False,
                                    'primaryKey': 1
                                },
                                {
                                    'columnName': 'price',
                                    'displayName': '価格',
                                    'columnType': {
                                        'columnType': 'DECIMAL(10,2)',
                                        'baseType': 'DECIMAL',
                                        'precision': 10,
                                        'scale': 2
                                    },
                                    'nullable': False
                                }
                            ]
                        }
                    }
                }
            }
        }

        # Write test data
        with open(self.schema_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(schema_data, f, allow_unicode=True)

        # Test load
        schema_manager = SchemaManager.load(self.schema_yaml_path)

        main_schema = schema_manager['main']
        products_table = main_schema.tables['products']

        self.assertEqual(products_table.display_name, '商品')
        self.assertEqual(len(products_table.columns), 2)

        # Test column types
        id_column = products_table.columns['id']
        self.assertEqual(id_column.column_type.base_type, 'BIGINT')

        price_column = products_table.columns['price']
        self.assertEqual(price_column.column_type.base_type, 'DECIMAL')
        self.assertEqual(price_column.column_type.precision, 10)
        self.assertEqual(price_column.column_type.scale, 2)

    def test_schema_roundtrip(self):
        """Test SchemaManager save/load roundtrip"""
        # Create complex schema
        schema_manager = SchemaManager()

        main_schema = Schema(name='main')
        schema_manager.schemas['main'] = main_schema

        # Create table with various column types
        test_table = Table(
            instance='main',
            table_name='test_table',
            display_name='テストテーブル'
        )

        # Add different column types
        columns_data = [
            ('id', 'ID', ColumnType(column_type='BIGINT', base_type='BIGINT'), False, 1),
            ('name', '名前', ColumnType(column_type='VARCHAR(255)', base_type='VARCHAR', length=255), False, None),
            ('price', '価格', ColumnType(column_type='DECIMAL(10,2)', base_type='DECIMAL', precision=10, scale=2), True, None),
            ('status', 'ステータス', ColumnType(column_type="ENUM('active','inactive')", base_type='ENUM', items=[
                ColumnTypeItem.from_string('active'),
                ColumnTypeItem.from_string('inactive')
            ]), False, None)
        ]

        for col_name, display_name, col_type, nullable, pk in columns_data:
            column = Column(
                column_name=col_name,
                display_name=display_name,
                column_type=col_type,
                nullable=nullable,
                primary_key=pk
            )
            test_table.columns.append(column)

        main_schema.tables_['test_table'] = test_table

        # Save
        schema_manager.save(self.schema_yaml_path)

        # Load
        loaded_schema_manager = SchemaManager.load(self.schema_yaml_path)

        # Verify
        loaded_table = loaded_schema_manager['main'].tables['test_table']
        self.assertEqual(loaded_table.display_name, 'テストテーブル')
        self.assertEqual(len(loaded_table.columns), 4)

        # Verify complex column types
        price_column = loaded_table.columns['price']
        self.assertEqual(price_column.column_type.precision, 10)
        self.assertEqual(price_column.column_type.scale, 2)

        status_column = loaded_table.columns['status']
        self.assertEqual(len(status_column.column_type.items), 2)
        self.assertEqual(status_column.column_type.items[0].value, 'active')
        self.assertEqual(status_column.column_type.items[1].value, 'inactive')


if __name__ == "__main__":
    unittest.main()
