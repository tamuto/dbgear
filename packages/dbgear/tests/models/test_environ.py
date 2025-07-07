import unittest
import tempfile
import os
import yaml

from dbgear.models.environ import EnvironManager, Environ
from dbgear.models.exceptions import DBGearEntityRemovalError


class TestEnviron(unittest.TestCase):
    """Test EnvironManager file I/O operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.env_name = 'test_env'

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_environ_add_and_load(self):
        """Test Environ add and load operations"""
        # Create test environ
        environ = Environ(
            folder=self.temp_dir,
            name=self.env_name,
            description='Test environment for testing',
            deployment={'production': 'mysql://user:pass@prod-host:3306/mydb', 'development': 'mysql://user:pass@dev-host:3306/mydb'}
        )
        environ.save()

        # Verify file exists
        environ_file = os.path.join(self.temp_dir, self.env_name, 'environ.yaml')
        self.assertTrue(os.path.exists(environ_file))

        # Verify file content
        with open(environ_file, 'r', encoding='utf-8') as f:
            saved_data = yaml.safe_load(f)

        self.assertEqual(saved_data['description'], 'Test environment for testing')
        self.assertEqual(saved_data['deployment']['production'], 'mysql://user:pass@prod-host:3306/mydb')
        self.assertEqual(saved_data['deployment']['development'], 'mysql://user:pass@dev-host:3306/mydb')

        # Test load
        environ_manager = EnvironManager(self.temp_dir)
        loaded_environ = environ_manager[self.env_name]
        self.assertEqual(loaded_environ.name, self.env_name)
        self.assertEqual(loaded_environ.description, 'Test environment for testing')
        self.assertEqual(loaded_environ.folder, self.temp_dir)
        self.assertEqual(loaded_environ.deployment['production'], 'mysql://user:pass@prod-host:3306/mydb')
        self.assertEqual(loaded_environ.deployment['development'], 'mysql://user:pass@dev-host:3306/mydb')

    def test_environ_load_from_existing_file(self):
        """Test loading Environ from existing YAML file"""
        # Create directory structure
        env_dir = os.path.join(self.temp_dir, 'production')
        os.makedirs(env_dir)

        # Create test environ data
        environ_data = {
            'description': 'Production environment',
            'deployment': {'production': 'mysql://prod:secret@prod-db:3306/app', 'staging': 'mysql://stage:secret@stage-db:3306/app'}
        }

        # Write test data
        environ_file = os.path.join(env_dir, 'environ.yaml')
        with open(environ_file, 'w', encoding='utf-8') as f:
            yaml.dump(environ_data, f, allow_unicode=True)

        # Test load
        environ_manager = EnvironManager(self.temp_dir)
        loaded_environ = environ_manager['production']

        self.assertEqual(loaded_environ.name, 'production')
        self.assertEqual(loaded_environ.description, 'Production environment')
        self.assertEqual(loaded_environ.folder, self.temp_dir)
        self.assertEqual(loaded_environ.deployment['production'], 'mysql://prod:secret@prod-db:3306/app')
        self.assertEqual(loaded_environ.deployment['staging'], 'mysql://stage:secret@stage-db:3306/app')

    def test_environ_manager_iteration(self):
        """Test EnvironManager iteration"""
        # Create multiple environments
        envs_data = [
            ('development', 'Development environment'),
            ('staging', 'Staging environment'),
            ('production', 'Production environment')
        ]

        environ_manager = EnvironManager(self.temp_dir)

        for name, desc in envs_data:
            environ = Environ(
                folder=self.temp_dir,
                name=name,
                description=desc,
                deployment={name: f'mysql://user:pass@{name}-db:3306/app'}
            )
            environ.save()

        # Test iteration
        loaded_environs = list(environ_manager)
        self.assertEqual(len(loaded_environs), 3)

        # Verify environments are loaded correctly
        env_names = [env.name for env in loaded_environs]
        self.assertIn('development', env_names)
        self.assertIn('staging', env_names)
        self.assertIn('production', env_names)

    def test_environ_remove_operations(self):
        """Test environ remove operations"""
        # Add environ
        environ = Environ(
            folder=self.temp_dir,
            name='removable',
            description='Environment to be removed'
        )
        environ.save()

        # Verify it exists
        env_path = os.path.join(self.temp_dir, 'removable')
        self.assertTrue(os.path.exists(env_path))

        # Test successful remove
        environ.delete()
        self.assertFalse(os.path.exists(env_path))

        # Test remove with extra files (should fail)
        environ.save()

        # Add extra file
        extra_file = os.path.join(env_path, 'extra_file.txt')
        with open(extra_file, 'w') as f:
            f.write('extra content')

        with self.assertRaises(DBGearEntityRemovalError):
            environ.delete()

    def test_environ_roundtrip(self):
        """Test environ add/load roundtrip"""
        # Create environ
        original_environ = Environ(
            folder=self.temp_dir,
            name='roundtrip_test',
            description='テスト環境の説明',
            deployment={'test': 'mysql://test:password@test-server:3306/testdb', 'local': 'sqlite:///local.db'}
        )
        original_environ.save()

        # Add and load
        environ_manager = EnvironManager(self.temp_dir)
        loaded_environ = environ_manager['roundtrip_test']

        # Verify all fields
        self.assertEqual(loaded_environ.name, original_environ.name)
        self.assertEqual(loaded_environ.description, original_environ.description)
        self.assertEqual(loaded_environ.folder, original_environ.folder)
        self.assertEqual(loaded_environ.deployment, original_environ.deployment)


if __name__ == "__main__":
    unittest.main()
