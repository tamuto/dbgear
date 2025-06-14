import unittest
from unittest.mock import MagicMock, patch, call

from dbgear.core.definitions.mysql import retrieve, build_fields, build_statistics
from dbgear.core.models.schema import Field, Index


class MockRow:
    """Mock database row for testing"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestMySQLDefinitions(unittest.TestCase):
    """Test cases for MySQL definition parser"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_connection = MagicMock()
        self.test_mapping = {
            'test_db': 'main'
        }

    @patch('dbgear.core.definitions.mysql.describe')
    def test_build_fields_basic(self, mock_describe):
        """Test basic field building from database metadata"""
        # Mock column data
        mock_columns = [
            MockRow(
                COLUMN_NAME='id',
                COLUMN_TYPE='int(11)',
                IS_NULLABLE='NO',
                COLUMN_KEY='PRI',
                COLUMN_DEFAULT=None,
                COLUMN_COMMENT='Primary key'
            ),
            MockRow(
                COLUMN_NAME='name',
                COLUMN_TYPE='varchar(100)',
                IS_NULLABLE='YES',
                COLUMN_KEY='',
                COLUMN_DEFAULT=None,
                COLUMN_COMMENT='User name'
            ),
            MockRow(
                COLUMN_NAME='email',
                COLUMN_TYPE='varchar(255)',
                IS_NULLABLE='NO',
                COLUMN_KEY='UNI',
                COLUMN_DEFAULT=None,
                COLUMN_COMMENT=''
            )
        ]

        mock_describe.columns.return_value = mock_columns

        # Test field building
        fields = build_fields(self.mock_connection, 'test_db', 'users', {'id': 1})

        # Verify describe.columns was called correctly
        mock_describe.columns.assert_called_once_with(self.mock_connection, 'test_db', 'users')

        # Verify field results
        self.assertEqual(len(fields), 3)

        # Check primary key field
        id_field = fields[0]
        self.assertEqual(id_field.column_name, 'id')
        self.assertEqual(id_field.column_type, 'int(11)')
        self.assertFalse(id_field.nullable)
        self.assertEqual(id_field.primary_key, 1)
        self.assertEqual(id_field.comment, 'Primary key')

        # Check nullable field
        name_field = fields[1]
        self.assertEqual(name_field.column_name, 'name')
        self.assertEqual(name_field.column_type, 'varchar(100)')
        self.assertTrue(name_field.nullable)
        self.assertIsNone(name_field.primary_key)
        self.assertEqual(name_field.comment, 'User name')

        # Check unique field
        email_field = fields[2]
        self.assertEqual(email_field.column_name, 'email')
        self.assertEqual(email_field.column_type, 'varchar(255)')
        self.assertFalse(email_field.nullable)
        self.assertIsNone(email_field.primary_key)
        self.assertEqual(email_field.comment, '')

    @patch('dbgear.core.definitions.mysql.describe')
    def test_build_statistics_primary_and_indexes(self, mock_describe):
        """Test building primary keys and indexes from database metadata"""
        # Mock index data
        mock_indexes = [
            MockRow(
                INDEX_NAME='PRIMARY',
                NON_UNIQUE=0,
                COLUMN_NAME='id',
                SEQ_IN_INDEX=1
            ),
            MockRow(
                INDEX_NAME='idx_email',
                NON_UNIQUE=0,
                COLUMN_NAME='email',
                SEQ_IN_INDEX=1
            ),
            MockRow(
                INDEX_NAME='idx_name_email',
                NON_UNIQUE=1,
                COLUMN_NAME='name',
                SEQ_IN_INDEX=1
            ),
            MockRow(
                INDEX_NAME='idx_name_email',
                NON_UNIQUE=1,
                COLUMN_NAME='email',
                SEQ_IN_INDEX=2
            )
        ]

        mock_describe.indexes.return_value = mock_indexes

        # Test statistics building
        primary_key, indexes = build_statistics(self.mock_connection, 'test_db', 'users')

        # Verify describe.indexes was called correctly
        mock_describe.indexes.assert_called_once_with(self.mock_connection, 'test_db', 'users')

        # Check primary key
        self.assertEqual(primary_key, {'id': 1})

        # Check indexes
        self.assertEqual(len(indexes), 2)

        # Check unique index
        self.assertIn('idx_email', indexes)
        email_index = indexes['idx_email']
        self.assertEqual(email_index.index_name, 'idx_email')
        self.assertEqual(email_index.columns, ['email'])

        # Check multi-column index
        self.assertIn('idx_name_email', indexes)
        compound_index = indexes['idx_name_email']
        self.assertEqual(compound_index.index_name, 'idx_name_email')
        self.assertEqual(compound_index.columns, ['name', 'email'])

    @patch('dbgear.core.definitions.mysql.build_statistics')
    @patch('dbgear.core.definitions.mysql.build_fields')
    @patch('dbgear.core.definitions.mysql.describe')
    @patch('dbgear.core.definitions.mysql.engine')
    def test_retrieve_full_schema(self, mock_engine, mock_describe, mock_build_fields, mock_build_statistics):
        """Test full schema retrieval from database"""
        # Mock engine and connection
        mock_engine.get_connection.return_value.__enter__.return_value = self.mock_connection

        # Mock table discovery
        mock_tables = [
            MockRow(TABLE_NAME='users'),
            MockRow(TABLE_NAME='orders'),
            MockRow(TABLE_NAME='products')
        ]
        mock_describe.tables.return_value = mock_tables

        # Mock fields and statistics for each table
        mock_build_fields.side_effect = [
            [
                Field(
                    column_name='id', display_name='id', column_type='int(11)',
                    nullable=False, primary_key=1, default_value=None, foreign_key=None, comment='')
            ],
            [
                Field(
                    column_name='id', display_name='id', column_type='int(11)',
                    nullable=False, primary_key=1, default_value=None, foreign_key=None, comment=''),
                Field(
                    column_name='user_id', display_name='user_id', column_type='int(11)',
                    nullable=False, primary_key=None, default_value=None, foreign_key=None, comment='')
            ],
            [
                Field(
                    column_name='id', display_name='id', column_type='int(11)',
                    nullable=False, primary_key=1, default_value=None, foreign_key=None, comment=''),
                Field(
                    column_name='name', display_name='name', column_type='varchar(255)',
                    nullable=False, primary_key=None, default_value=None, foreign_key=None, comment='')
            ]
        ]

        mock_build_statistics.side_effect = [
            ({'id': 1}, {}),
            ({'id': 1}, {'idx_user': Index(index_name='idx_user', columns=['user_id'])}),
            ({'id': 1}, {})
        ]

        # Test retrieve function
        schemas = retrieve('test_folder', 'mysql+pymysql://user:pass@localhost/test_db', self.test_mapping)

        # Verify engine creation
        mock_engine.get_connection.assert_called_once_with('mysql+pymysql://user:pass@localhost/test_db')

        # Verify table discovery
        mock_describe.tables.assert_called_once_with(self.mock_connection, 'test_db')

        # Verify field and statistics building for each table
        expected_field_calls = [
            call(self.mock_connection, 'test_db', 'users', {'id': 1}),
            call(self.mock_connection, 'test_db', 'orders', {'id': 1}),
            call(self.mock_connection, 'test_db', 'products', {'id': 1})
        ]
        mock_build_fields.assert_has_calls(expected_field_calls)
        mock_build_statistics.assert_has_calls([
            call(self.mock_connection, 'test_db', 'users'),
            call(self.mock_connection, 'test_db', 'orders'),
            call(self.mock_connection, 'test_db', 'products')
        ])

        # Verify schema results (returns dict, not list)
        self.assertEqual(len(schemas), 1)

        schema = schemas['main']
        self.assertEqual(schema.name, 'main')
        self.assertEqual(len(schema.tables), 3)

        # Check table names
        table_names = list(schema.tables.keys())
        self.assertIn('users', table_names)
        self.assertIn('orders', table_names)
        self.assertIn('products', table_names)

        # Check orders table has index
        orders_table = schema.tables['orders']
        self.assertEqual(len(orders_table.indexes), 1)
        self.assertEqual(orders_table.indexes[0].index_name, 'idx_user')

    @patch('dbgear.core.definitions.mysql.describe')
    def test_build_fields_empty_result(self, mock_describe):
        """Test handling of empty column results"""
        mock_describe.columns.return_value = []

        fields = build_fields(self.mock_connection, 'test_db', 'empty_table', [])

        self.assertEqual(len(fields), 0)

    @patch('dbgear.core.definitions.mysql.describe')
    def test_build_statistics_no_indexes(self, mock_describe):
        """Test handling of tables with no indexes"""
        mock_describe.indexes.return_value = []

        primary_key, indexes = build_statistics(self.mock_connection, 'test_db', 'no_index_table')

        self.assertEqual(primary_key, {})
        self.assertEqual(len(indexes), 0)

    @patch('dbgear.core.definitions.mysql.describe')
    def test_build_statistics_primary_key_only(self, mock_describe):
        """Test handling of tables with only primary key"""
        mock_indexes = [
            MockRow(
                INDEX_NAME='PRIMARY',
                NON_UNIQUE=0,
                COLUMN_NAME='id',
                SEQ_IN_INDEX=1
            )
        ]
        mock_describe.indexes.return_value = mock_indexes

        primary_key, indexes = build_statistics(self.mock_connection, 'test_db', 'simple_table')

        self.assertEqual(primary_key, {'id': 1})
        self.assertEqual(len(indexes), 0)

    @patch('dbgear.core.definitions.mysql.describe')
    def test_build_statistics_composite_primary_key(self, mock_describe):
        """Test handling of composite primary keys"""
        mock_indexes = [
            MockRow(
                INDEX_NAME='PRIMARY',
                NON_UNIQUE=0,
                COLUMN_NAME='user_id',
                SEQ_IN_INDEX=1
            ),
            MockRow(
                INDEX_NAME='PRIMARY',
                NON_UNIQUE=0,
                COLUMN_NAME='product_id',
                SEQ_IN_INDEX=2
            )
        ]
        mock_describe.indexes.return_value = mock_indexes

        primary_key, indexes = build_statistics(self.mock_connection, 'test_db', 'composite_table')

        self.assertEqual(primary_key, {'user_id': 1, 'product_id': 2})
        self.assertEqual(len(indexes), 0)

    @patch('dbgear.core.definitions.mysql.engine')
    def test_retrieve_connection_error(self, mock_engine):
        """Test handling of database connection errors"""
        mock_engine.get_connection.side_effect = Exception("Connection failed")

        with self.assertRaises(Exception) as context:
            retrieve('test_folder', 'mysql+pymysql://invalid:connection@localhost/test_db', self.test_mapping)

        self.assertIn("Connection failed", str(context.exception))

    @patch('dbgear.core.definitions.mysql.build_statistics')
    @patch('dbgear.core.definitions.mysql.build_fields')
    @patch('dbgear.core.definitions.mysql.describe')
    @patch('dbgear.core.definitions.mysql.engine')
    def test_retrieve_multiple_schemas(self, mock_engine, mock_describe, mock_build_fields, mock_build_statistics):
        """Test retrieval with multiple database schemas mapped to different instances"""
        # Mock engine and connection
        mock_engine.get_connection.return_value.__enter__.return_value = self.mock_connection

        # Test mapping with multiple schemas
        multi_mapping = {
            'db1': 'main',
            'db2': 'secondary'
        }

        # Mock different tables for each schema
        mock_describe.tables.side_effect = [
            [MockRow(TABLE_NAME='users')],  # db1 tables
            [MockRow(TABLE_NAME='logs')]    # db2 tables
        ]

        mock_build_fields.side_effect = [
            [Field(
                column_name='id', display_name='id', column_type='int(11)',
                nullable=False, primary_key=1, default_value=None, foreign_key=None, comment='')],  # db1.users
            [Field(
                column_name='id', display_name='id', column_type='int(11)',
                nullable=False, primary_key=1, default_value=None, foreign_key=None, comment='')]   # db2.logs
        ]

        mock_build_statistics.side_effect = [
            ({'id': 1}, {}),  # db1.users
            ({'id': 1}, {})   # db2.logs
        ]

        # Test retrieve function
        schemas = retrieve('test_folder', 'mysql+pymysql://user:pass@localhost', multi_mapping)

        # Verify two schemas returned
        self.assertEqual(len(schemas), 2)

        # Check schema instances
        self.assertIn('main', schemas)
        self.assertIn('secondary', schemas)

        # Verify describe.tables called for each schema
        expected_calls = [
            call(self.mock_connection, 'db1'),
            call(self.mock_connection, 'db2')
        ]
        mock_describe.tables.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest.main()
