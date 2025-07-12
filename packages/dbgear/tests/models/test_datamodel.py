import unittest
import tempfile
import os
import shutil

from dbgear.models.datamodel import DataModel
from dbgear.utils.const import DATATYPE_YAML


class TestDataModel(unittest.TestCase):
    """Test DataModel YAML file I/O operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.environ_dir = os.path.join(self.temp_dir, 'development')
        os.makedirs(self.environ_dir, exist_ok=True)
        self.base_dir = os.path.join(self.environ_dir, 'base')
        os.makedirs(self.base_dir, exist_ok=True)
        self.datamodel_yaml_path = os.path.join(self.base_dir, 'main@users.yaml')

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_datamodel_save_and_load(self):
        """Test DataModel save and load operations"""
        # Create test data model
        datamodel = DataModel(
            folder=self.temp_dir,
            environ='development',
            map_name='base',
            schema_name='main',
            table_name='users',
            description='User management',
            sync_mode='manual',
            data_type=DATATYPE_YAML,
        )

        # Test save
        datamodel.save()
        self.assertTrue(os.path.exists(self.datamodel_yaml_path))

        # Test load
        loaded_datamodel = DataModel.load(self.temp_dir, 'development', 'base', 'main', 'users')
        self.assertEqual(loaded_datamodel.schema_name, 'main')
        self.assertEqual(loaded_datamodel.table_name, 'users')
        self.assertEqual(loaded_datamodel.description, 'User management')
        self.assertEqual(loaded_datamodel.sync_mode, 'manual')
        self.assertEqual(loaded_datamodel.data_type, DATATYPE_YAML)


if __name__ == "__main__":
    unittest.main()
