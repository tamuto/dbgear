import unittest
import tempfile
import os
import yaml
import shutil

from dbgear.models.datamodel import DataModel, SettingInfo
from dbgear.models.const import SETTING_TYPE_COLUMN, SETTING_TYPE_REF


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
        settings = {
            'id': SettingInfo(type=SETTING_TYPE_COLUMN, width=50),
            'name': SettingInfo(type=SETTING_TYPE_COLUMN, width=200)
        }

        datamodel = DataModel(
            folder=self.temp_dir,
            environ='development',
            map_name='base',
            schema_name='main',
            table_name='users',
            description='User management',
            layout='table',
            settings=settings,
            sync_mode='manual'
        )

        # Test save
        datamodel.save()
        self.assertTrue(os.path.exists(self.datamodel_yaml_path))

        # Test load  
        loaded_datamodel = DataModel.load(self.temp_dir, 'development', 'base', 'main', 'users')
        self.assertEqual(loaded_datamodel.schema_name, 'main')
        self.assertEqual(loaded_datamodel.table_name, 'users')
        self.assertEqual(loaded_datamodel.description, 'User management')
        self.assertEqual(loaded_datamodel.layout, 'table')
        self.assertEqual(len(loaded_datamodel.settings), 2)

    def test_datamodel_load_from_existing_yaml(self):
        """Test loading DataModel from existing YAML file"""
        # Create test YAML data with enum settings
        datamodel_data = {
            'schemaName': 'main',
            'tableName': 'products',
            'description': 'Product catalog',
            'layout': 'grid',
            'settings': {
                'id': {'type': 'column', 'width': 50},
                'user_ref': {'type': 'ref', 'tableName': 'users'}
            },
            'syncMode': 'auto'
        }

        # Write test data
        products_yaml_path = os.path.join(self.base_dir, 'main@products.yaml')
        with open(products_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(datamodel_data, f, allow_unicode=True)

        # Test load
        datamodel = DataModel.load(self.temp_dir, 'development', 'base', 'main', 'products')
        self.assertEqual(datamodel.schema_name, 'main')
        self.assertEqual(datamodel.table_name, 'products')
        self.assertEqual(datamodel.description, 'Product catalog')
        self.assertEqual(datamodel.sync_mode, 'auto')
        
        # Test settings are properly loaded
        self.assertEqual(len(datamodel.settings), 2)
        self.assertEqual(datamodel.settings['id'].type, SETTING_TYPE_COLUMN)
        self.assertEqual(datamodel.settings['id'].width, 50)
        self.assertEqual(datamodel.settings['user_ref'].type, SETTING_TYPE_REF)
        self.assertEqual(datamodel.settings['user_ref'].table_name, 'users')

    def test_datamodel_roundtrip(self):
        """Test DataModel save/load roundtrip"""
        # Create original data model
        settings = {
            'id': SettingInfo(type=SETTING_TYPE_COLUMN, width=50),
            'user_ref': SettingInfo(type=SETTING_TYPE_REF, table_name='users')
        }

        original = DataModel(
            folder=self.temp_dir,
            environ='development',
            map_name='base',
            schema_name='main',
            table_name='orders',
            description='Order management',
            layout='dashboard',
            settings=settings,
            sync_mode='auto',
            caption='Order Dashboard'
        )

        # Save
        original.save()

        # Load
        loaded = DataModel.load(self.temp_dir, 'development', 'base', 'main', 'orders')

        # Verify
        self.assertEqual(original.schema_name, loaded.schema_name)
        self.assertEqual(original.table_name, loaded.table_name)
        self.assertEqual(original.description, loaded.description)
        self.assertEqual(original.layout, loaded.layout)
        self.assertEqual(original.sync_mode, loaded.sync_mode)
        self.assertEqual(original.caption, loaded.caption)
        self.assertEqual(len(loaded.settings), 2)
        
        # Verify settings roundtrip correctly
        self.assertEqual(loaded.settings['id'].type, SETTING_TYPE_COLUMN)
        self.assertEqual(loaded.settings['id'].width, 50)
        self.assertEqual(loaded.settings['user_ref'].type, SETTING_TYPE_REF)
        self.assertEqual(loaded.settings['user_ref'].table_name, 'users')


if __name__ == "__main__":
    unittest.main()