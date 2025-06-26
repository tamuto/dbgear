import unittest
import tempfile
import os
import yaml

from dbgear.models.mapping import MappingManager, Mapping
from dbgear.models.exceptions import DBGearEntityExistsError, DBGearEntityNotFoundError, DBGearEntityRemovalError


class TestMapping(unittest.TestCase):
    """Test MappingManager file I/O operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.env_name = 'common'
        self.mapping_name = 'base'

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_mapping_add_and_load(self):
        """Test Mapping add and load operations"""
        # Create test mapping
        mapping = Mapping(
            folder=self.temp_dir,
            environ=self.env_name,
            name=self.mapping_name,
            description='Base mapping for testing',
            schemas=['main'],
            deploy=False
        )

        # Test add
        mapping_manager = MappingManager(self.temp_dir, self.env_name)
        mapping_manager.add(mapping)

        # Verify file exists
        mapping_file = os.path.join(self.temp_dir, self.env_name, self.mapping_name, '_mapping.yaml')
        self.assertTrue(os.path.exists(mapping_file))

        # Verify file content
        with open(mapping_file, 'r', encoding='utf-8') as f:
            saved_data = yaml.safe_load(f)

        self.assertEqual(saved_data['description'], 'Base mapping for testing')
        self.assertEqual(saved_data['schemas'], ['main'])
        # deploy=False is excluded by exclude_defaults
        self.assertEqual(saved_data.get('deploy', False), False)

        # Test load
        loaded_mapping = mapping_manager[self.mapping_name]
        self.assertEqual(loaded_mapping.description, 'Base mapping for testing')
        self.assertEqual(loaded_mapping.schemas, ['main'])
        self.assertFalse(loaded_mapping.deploy)

    def test_mapping_load_from_existing_file(self):
        """Test loading Mapping from existing YAML file"""
        # Create directory structure
        mapping_dir = os.path.join(self.temp_dir, self.env_name, 'test1')
        os.makedirs(mapping_dir)

        # Create test mapping data
        mapping_data = {
            'description': 'テスト1データベース',
            'schemas': ['main'],
            'deploy': True,
        }

        # Write test data
        mapping_file = os.path.join(mapping_dir, '_mapping.yaml')
        with open(mapping_file, 'w', encoding='utf-8') as f:
            yaml.dump(mapping_data, f, allow_unicode=True)

        # Test load
        mapping_manager = MappingManager(self.temp_dir, self.env_name)
        loaded_mapping = mapping_manager['test1']

        self.assertEqual(loaded_mapping.description, 'テスト1データベース')
        self.assertEqual(loaded_mapping.schemas, ['main'])
        self.assertTrue(loaded_mapping.deploy)

    def test_mapping_manager_iteration(self):
        """Test MappingManager iteration"""
        # Create multiple mappings
        mappings_data = [
            ('base', 'Base mapping', False),
            ('test1', 'Test 1 mapping', True),
            ('test2', 'Test 2 mapping', False)
        ]

        mapping_manager = MappingManager(self.temp_dir, self.env_name)

        for name, desc, deploy in mappings_data:
            mapping = Mapping(
                folder=self.temp_dir,
                environ=self.env_name,
                name=name,
                description=desc,
                instances=['main'],
                deploy=deploy
            )
            mapping_manager.add(mapping)

        # Test iteration
        loaded_mappings = list(mapping_manager)
        self.assertEqual(len(loaded_mappings), 3)

        # Verify mappings are loaded correctly
        mapping_names = [m.name for m in loaded_mappings]
        self.assertIn('base', mapping_names)
        self.assertIn('test1', mapping_names)
        self.assertIn('test2', mapping_names)

    def test_mapping_manager_exceptions(self):
        """Test MappingManager exception handling"""
        mapping_manager = MappingManager(self.temp_dir, self.env_name)

        # Test add duplicate
        mapping1 = Mapping(
            folder=self.temp_dir,
            environ=self.env_name,
            name='duplicate',
            description='First mapping'
        )
        mapping_manager.add(mapping1)

        mapping2 = Mapping(
            folder=self.temp_dir,
            environ=self.env_name,
            name='duplicate',
            description='Second mapping'
        )

        with self.assertRaises(DBGearEntityExistsError):
            mapping_manager.add(mapping2)

        # Test load nonexistent
        with self.assertRaises(FileNotFoundError):
            mapping_manager['nonexistent']

        # Test remove nonexistent
        with self.assertRaises(DBGearEntityNotFoundError):
            mapping_manager.remove('nonexistent')

    def test_mapping_remove_operations(self):
        """Test mapping remove operations"""
        mapping_manager = MappingManager(self.temp_dir, self.env_name)

        # Add mapping
        mapping = Mapping(
            folder=self.temp_dir,
            environ=self.env_name,
            name='removable',
            description='Mapping to be removed'
        )
        mapping_manager.add(mapping)

        # Verify it exists
        mapping_path = os.path.join(self.temp_dir, self.env_name, 'removable')
        self.assertTrue(os.path.exists(mapping_path))

        # Test successful remove
        mapping_manager.remove('removable')
        self.assertFalse(os.path.exists(mapping_path))

        # Test remove with extra files (should fail)
        mapping_manager.add(mapping)  # Re-add

        # Add extra file
        extra_file = os.path.join(mapping_path, 'extra_file.txt')
        with open(extra_file, 'w') as f:
            f.write('extra content')

        with self.assertRaises(DBGearEntityRemovalError):
            mapping_manager.remove('removable')

    def test_mapping_roundtrip(self):
        """Test mapping add/load roundtrip"""
        # Create complex mapping
        original_mapping = Mapping(
            folder=self.temp_dir,
            environ=self.env_name,
            name='complex',
            description='複雑なマッピング設定',
            instances=['main', 'sub'],
            deploy=True,
        )

        # Add and load
        mapping_manager = MappingManager(self.temp_dir, self.env_name)
        mapping_manager.add(original_mapping)
        loaded_mapping = mapping_manager['complex']

        # Verify all fields
        self.assertEqual(loaded_mapping.description, original_mapping.description)
        self.assertEqual(loaded_mapping.schemas, original_mapping.schemas)
        self.assertEqual(loaded_mapping.deploy, original_mapping.deploy)


if __name__ == "__main__":
    unittest.main()
