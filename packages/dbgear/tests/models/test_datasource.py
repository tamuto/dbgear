import unittest
import tempfile
import os
import yaml
import shutil

from dbgear.models.datamodel import DataSource


class TestDataSource(unittest.TestCase):
    """Test DataSource YAML file I/O operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.environ_dir = os.path.join(self.temp_dir, 'development')
        os.makedirs(self.environ_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_datasource_save_and_load(self):
        """Test DataSource save and load operations"""
        # Create test DataSource
        datasource = DataSource()
        datasource.folder = self.temp_dir
        datasource.environ = 'development'
        datasource.schema_name = 'main'
        datasource.table_name = 'users'
        datasource.data = [
            {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
        ]

        # Test save
        datasource.save()
        expected_path = os.path.join(self.environ_dir, 'main@users.dat')
        self.assertTrue(os.path.exists(expected_path))

        # Test load
        loaded_datasource = DataSource()
        loaded_datasource.folder = self.temp_dir
        loaded_datasource.environ = 'development'
        loaded_datasource.schema_name = 'main'
        loaded_datasource.table_name = 'users'
        loaded_datasource.load()

        self.assertEqual(len(loaded_datasource.data), 2)
        self.assertEqual(loaded_datasource.data[0]['name'], 'Alice')
        self.assertEqual(loaded_datasource.data[1]['email'], 'bob@example.com')

    def test_datasource_load_from_existing_file(self):
        """Test loading DataSource from existing data file"""
        # Create test data file
        test_data = [
            {'product_id': 1, 'name': 'Product A', 'price': 100.0},
            {'product_id': 2, 'name': 'Product B', 'price': 200.0}
        ]

        data_file_path = os.path.join(self.environ_dir, 'main@products.dat')
        with open(data_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True)

        # Test load
        datasource = DataSource()
        datasource.folder = self.temp_dir
        datasource.environ = 'development'
        datasource.schema_name = 'main'
        datasource.table_name = 'products'
        datasource.load()

        self.assertEqual(len(datasource.data), 2)
        self.assertEqual(datasource.data[0]['name'], 'Product A')
        self.assertEqual(datasource.data[1]['price'], 200.0)

    def test_datasource_roundtrip(self):
        """Test DataSource save/load roundtrip"""
        # Create original DataSource
        original = DataSource()
        original.folder = self.temp_dir
        original.environ = 'development'
        original.schema_name = 'main'
        original.table_name = 'orders'
        original.data = [
            {'order_id': 1, 'customer': 'John', 'amount': 150.0, 'status': 'completed'},
            {'order_id': 2, 'customer': 'Jane', 'amount': 300.0, 'status': 'pending'}
        ]

        # Save
        original.save()

        # Load
        loaded = DataSource()
        loaded.folder = self.temp_dir
        loaded.environ = 'development'
        loaded.schema_name = 'main'
        loaded.table_name = 'orders'
        loaded.load()

        # Verify
        self.assertEqual(len(loaded.data), 2)
        self.assertEqual(loaded.data[0]['customer'], 'John')
        self.assertEqual(loaded.data[0]['amount'], 150.0)
        self.assertEqual(loaded.data[1]['status'], 'pending')

    def test_datasource_with_segment(self):
        """Test DataSource with segment functionality"""
        # Create DataSource with segment
        datasource = DataSource()
        datasource.folder = self.temp_dir
        datasource.environ = 'development'
        datasource.schema_name = 'main'
        datasource.table_name = 'sales'
        datasource.segment = '2024q1'
        datasource.data = [
            {'month': 'January', 'sales': 1000},
            {'month': 'February', 'sales': 1500}
        ]

        # Test filename generation
        self.assertEqual(datasource.filename, 'main@sales#2024q1.dat')

        # Test save and load
        datasource.save()
        expected_path = os.path.join(self.environ_dir, 'main@sales#2024q1.dat')
        self.assertTrue(os.path.exists(expected_path))

        # Load with segment
        loaded = DataSource()
        loaded.folder = self.temp_dir
        loaded.environ = 'development'
        loaded.schema_name = 'main'
        loaded.table_name = 'sales'
        loaded.segment = '2024q1'
        loaded.load()

        self.assertEqual(len(loaded.data), 2)
        self.assertEqual(loaded.data[0]['month'], 'January')

    def test_datasource_load_file_not_found(self):
        """Test DataSource load with non-existent file raises FileNotFoundError"""
        datasource = DataSource()
        datasource.folder = self.temp_dir
        datasource.environ = 'development'
        datasource.schema_name = 'nonexistent'
        datasource.table_name = 'table'

        with self.assertRaises(FileNotFoundError) as context:
            datasource.load()

        self.assertIn('does not exist', str(context.exception))


if __name__ == "__main__":
    unittest.main()