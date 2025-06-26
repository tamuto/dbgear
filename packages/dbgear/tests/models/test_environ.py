import unittest
import tempfile
import os
import yaml

from dbgear.models.environ import EnvironManager, Environ
from dbgear.models.exceptions import DBGearEntityExistsError, DBGearEntityNotFoundError, DBGearEntityRemovalError


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

        # Test add
        environ_manager = EnvironManager(self.temp_dir)
        environ_manager.add(environ)

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
            environ_manager.add(environ)

        # Test iteration
        loaded_environs = list(environ_manager)
        self.assertEqual(len(loaded_environs), 3)

        # Verify environments are loaded correctly
        env_names = [env.name for env in loaded_environs]
        self.assertIn('development', env_names)
        self.assertIn('staging', env_names)
        self.assertIn('production', env_names)

    def test_environ_manager_exceptions(self):
        """Test EnvironManager exception handling"""
        environ_manager = EnvironManager(self.temp_dir)

        # Test add duplicate
        environ1 = Environ(
            folder=self.temp_dir,
            name='duplicate',
            description='First environment'
        )
        environ_manager.add(environ1)

        environ2 = Environ(
            folder=self.temp_dir,
            name='duplicate',
            description='Second environment'
        )

        with self.assertRaises(DBGearEntityExistsError):
            environ_manager.add(environ2)

        # Test load nonexistent
        with self.assertRaises(FileNotFoundError):
            environ_manager['nonexistent']

        # Test remove nonexistent
        with self.assertRaises(DBGearEntityNotFoundError):
            environ_manager.remove('nonexistent')

    def test_environ_remove_operations(self):
        """Test environ remove operations"""
        environ_manager = EnvironManager(self.temp_dir)

        # Add environ
        environ = Environ(
            folder=self.temp_dir,
            name='removable',
            description='Environment to be removed'
        )
        environ_manager.add(environ)

        # Verify it exists
        env_path = os.path.join(self.temp_dir, 'removable')
        self.assertTrue(os.path.exists(env_path))

        # Test successful remove
        environ_manager.remove('removable')
        self.assertFalse(os.path.exists(env_path))

        # Test remove with extra files (should fail)
        environ_manager.add(environ)  # Re-add

        # Add extra file
        extra_file = os.path.join(env_path, 'extra_file.txt')
        with open(extra_file, 'w') as f:
            f.write('extra content')

        with self.assertRaises(DBGearEntityRemovalError):
            environ_manager.remove('removable')

    def test_environ_lazy_loading_properties(self):
        """Test environ lazy loading properties"""
        # Create environment with related files
        environ_manager = EnvironManager(self.temp_dir)
        environ = Environ(
            folder=self.temp_dir,
            name='lazy_test',
            description='Test lazy loading'
        )
        environ_manager.add(environ)

        # Create schema.yaml
        env_dir = os.path.join(self.temp_dir, 'lazy_test')
        schema_file = os.path.join(env_dir, 'schema.yaml')
        schema_data = {
            'schemas': {
                'main': {
                    'tables': {}
                }
            }
        }
        with open(schema_file, 'w', encoding='utf-8') as f:
            yaml.dump(schema_data, f)

        # Create tenant.yaml
        tenant_file = os.path.join(env_dir, 'tenant.yaml')
        tenant_data = {
            'tenants': {
                'localhost': {
                    'name': 'localhost',
                    'ref': 'base'
                }
            }
        }
        with open(tenant_file, 'w', encoding='utf-8') as f:
            yaml.dump(tenant_data, f)

        # Load environ and test lazy properties
        loaded_environ = environ_manager['lazy_test']

        # Test schemas property (lazy loading)
        schemas = loaded_environ.schemas
        self.assertIsNotNone(schemas)
        self.assertIn('main', schemas.schemas)

        # Test tenants property (lazy loading)
        tenants = loaded_environ.tenants
        self.assertIsNotNone(tenants)
        self.assertIn('localhost', tenants.tenants)

        # Test mappings property
        mappings = loaded_environ.mappings
        self.assertIsNotNone(mappings)

    def test_environ_roundtrip(self):
        """Test environ add/load roundtrip"""
        # Create environ
        original_environ = Environ(
            folder=self.temp_dir,
            name='roundtrip_test',
            description='テスト環境の説明',
            deployment={'test': 'mysql://test:password@test-server:3306/testdb', 'local': 'sqlite:///local.db'}
        )

        # Add and load
        environ_manager = EnvironManager(self.temp_dir)
        environ_manager.add(original_environ)
        loaded_environ = environ_manager['roundtrip_test']

        # Verify all fields
        self.assertEqual(loaded_environ.name, original_environ.name)
        self.assertEqual(loaded_environ.description, original_environ.description)
        self.assertEqual(loaded_environ.folder, original_environ.folder)
        self.assertEqual(loaded_environ.deployment, original_environ.deployment)


if __name__ == "__main__":
    unittest.main()
