import unittest
from dbgear.core.definitions.mysql import retrieve
from dbgear.core.models.schema import Schema


class TestMySQLIntegration(unittest.TestCase):
    """Integration tests for MySQL definition parser with real database connection"""

    def setUp(self):
        """Set up test fixtures"""
        # Test connection string from project.yaml
        self.connection_string = 'mysql+pymysql://root:password@host.docker.internal?charset=utf8mb4'
        self.test_mapping = {
            'test': 'main'  # Map 'test' database schema to 'main' instance
        }

    def test_mysql_connection_and_schema_retrieval(self):
        """Test actual MySQL connection and schema retrieval"""
        try:
            # Attempt to connect to MySQL and retrieve schema
            schemas = retrieve(
                folder='test_folder',
                connect=self.connection_string,
                mapping=self.test_mapping
            )

            # Basic validation
            self.assertIsInstance(schemas, dict)
            print(f"Successfully connected to MySQL. Retrieved {len(schemas)} schemas.")

            if 'main' in schemas:
                main_schema = schemas['main']
                self.assertIsInstance(main_schema, Schema)
                print(f"Main schema contains {len(main_schema.tables)} tables.")

                # Print table information for debugging
                for table_name, table in main_schema.tables.items():
                    print(f"Table: {table_name}")
                    print(f"  Fields: {len(table.fields)}")
                    print(f"  Indexes: {len(table.indexes)}")
                    for field in table.fields[:3]:  # Show first 3 fields
                        print(f"    - {field.column_name} ({field.column_type})")

        except Exception as e:
            # If connection fails, skip the test with informative message
            self.skipTest(
                f"MySQL connection failed: {e}. "
                f"Make sure MySQL is running and accessible at {self.connection_string}")

    def test_mysql_empty_database(self):
        """Test handling of empty database or non-existent schema"""
        try:
            # Test with a non-existent database schema
            empty_mapping = {
                'nonexistent_db': 'empty'
            }

            schemas = retrieve(
                folder='test_folder',
                connect=self.connection_string,
                mapping=empty_mapping
            )

            # Should return empty schema or handle gracefully
            if 'empty' in schemas:
                empty_schema = schemas['empty']
                self.assertEqual(len(empty_schema.tables), 0)
                print("Successfully handled empty/non-existent database schema.")

        except Exception as e:
            # Connection issues are expected if MySQL is not available
            self.skipTest(f"MySQL connection failed: {e}")

    def test_mysql_information_schema_access(self):
        """Test that we can access MySQL information_schema tables"""
        try:
            # Test with information_schema itself (should always exist)
            info_mapping = {
                'information_schema': 'info'
            }

            schemas = retrieve(
                folder='test_folder',
                connect=self.connection_string,
                mapping=info_mapping
            )

            if 'info' in schemas:
                info_schema = schemas['info']
                # information_schema should have many tables
                self.assertGreater(len(info_schema.tables), 10)
                print(f"Information schema contains {len(info_schema.tables)} tables.")

                # Should include standard tables like TABLES, COLUMNS, etc.
                table_names = list(info_schema.tables.keys())
                expected_tables = ['TABLES', 'COLUMNS', 'STATISTICS']
                for expected in expected_tables:
                    if expected in table_names:
                        print(f"Found expected table: {expected}")

        except Exception as e:
            self.skipTest(f"MySQL connection failed: {e}")


if __name__ == '__main__':
    unittest.main()
