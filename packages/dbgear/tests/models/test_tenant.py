import unittest
import tempfile
import os
import yaml

from dbgear.models.tenant import TenantRegistry, TenantConfig, DatabaseInfo
from dbgear.models.exceptions import DBGearEntityExistsError, DBGearEntityNotFoundError


class TestTenant(unittest.TestCase):
    """Test TenantRegistry YAML file I/O operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.tenant_yaml_path = os.path.join(self.temp_dir, 'tenant.yaml')

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_tenant_registry_save_and_load(self):
        """Test TenantRegistry save and load operations"""
        # Create test tenant registry
        tenant_registry = TenantRegistry(folder=self.temp_dir, name='test_env')

        # Add test tenant
        db_info = DatabaseInfo(
            name='main',
            database='testdb',
            description='Test database',
            active=True
        )

        tenant_config = TenantConfig(
            name='localhost',
            ref='base',
            databases=[db_info]
        )

        tenant_registry.add(tenant_config)

        # Create the directory structure
        env_dir = os.path.join(self.temp_dir, 'test_env')
        os.makedirs(env_dir, exist_ok=True)

        # Test save
        tenant_registry.save()
        tenant_yaml_path = os.path.join(self.temp_dir, 'test_env', 'tenant.yaml')
        self.assertTrue(os.path.exists(tenant_yaml_path))

        # Test load
        loaded_registry = TenantRegistry.load(self.temp_dir, 'test_env')
        self.assertIn('localhost', loaded_registry.tenants)

        loaded_tenant = loaded_registry['localhost']
        self.assertEqual(loaded_tenant.name, 'localhost')
        self.assertEqual(loaded_tenant.ref, 'base')
        self.assertEqual(len(loaded_tenant.databases), 1)

        loaded_db = loaded_tenant.databases[0]
        self.assertEqual(loaded_db.name, 'main')
        self.assertEqual(loaded_db.database, 'testdb')
        self.assertTrue(loaded_db.active)

    def test_tenant_load_from_existing_yaml(self):
        """Test loading TenantRegistry from existing YAML file"""
        # Create directory structure
        env_dir = os.path.join(self.temp_dir, 'test_env')
        os.makedirs(env_dir)
        tenant_yaml_path = os.path.join(env_dir, 'tenant.yaml')
        
        # Create test tenant data
        tenant_data = {
            'tenants': {
                'production': {
                    'name': 'production',
                    'ref': 'production_base',
                    'databases': [
                        {
                            'name': 'main',
                            'database': 'prod_main',
                            'description': 'Production main database',
                            'active': True
                        },
                        {
                            'name': 'backup',
                            'database': 'prod_backup',
                            'description': 'Production backup database',
                            'active': False
                        }
                    ]
                }
            }
        }

        # Write test data
        with open(tenant_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(tenant_data, f, allow_unicode=True)

        # Test load
        tenant_registry = TenantRegistry.load(self.temp_dir, 'test_env')

        prod_tenant = tenant_registry['production']
        self.assertEqual(prod_tenant.name, 'production')
        self.assertEqual(prod_tenant.ref, 'production_base')
        self.assertEqual(len(prod_tenant.databases), 2)

        # Check databases
        main_db = next(db for db in prod_tenant.databases if db.name == 'main')
        self.assertTrue(main_db.active)

        backup_db = next(db for db in prod_tenant.databases if db.name == 'backup')
        self.assertFalse(backup_db.active)

    def test_tenant_registry_crud_operations(self):
        """Test TenantRegistry CRUD operations"""
        tenant_registry = TenantRegistry(folder=self.temp_dir, name='test_env')

        # Test add
        tenant1 = TenantConfig(name='tenant1', ref='base')
        tenant_registry.add(tenant1)
        self.assertIn('tenant1', tenant_registry.tenants)

        # Test duplicate add raises exception
        with self.assertRaises(DBGearEntityExistsError):
            tenant_registry.add(tenant1)

        # Test get
        retrieved_tenant = tenant_registry['tenant1']
        self.assertEqual(retrieved_tenant.name, 'tenant1')

        # Test contains
        self.assertTrue('tenant1' in tenant_registry)
        self.assertFalse('nonexistent' in tenant_registry)

        # Test length
        self.assertEqual(len(tenant_registry), 1)

        # Test iteration
        tenants_list = list(tenant_registry)
        self.assertEqual(len(tenants_list), 1)
        self.assertEqual(tenants_list[0].name, 'tenant1')

        # Test remove
        tenant_registry.remove('tenant1')
        self.assertNotIn('tenant1', tenant_registry.tenants)

        # Test remove nonexistent raises exception
        with self.assertRaises(DBGearEntityNotFoundError):
            tenant_registry.remove('nonexistent')

    def test_tenant_roundtrip(self):
        """Test TenantRegistry save/load roundtrip"""
        # Create complex tenant registry
        tenant_registry = TenantRegistry(folder=self.temp_dir, name='test_env')

        # Multiple tenants with different configurations
        tenants_data = [
            ('localhost', 'local_base', [
                ('main', 'local_main', 'Local main DB', True)
            ]),
            ('docker', 'docker_base', [
                ('main', 'docker_main', 'Docker main DB', True),
                ('test', 'docker_test', 'Docker test DB', False)
            ])
        ]

        for tenant_name, ref, dbs in tenants_data:
            databases = [
                DatabaseInfo(name=name, database=db, description=desc, active=active)
                for name, db, desc, active in dbs
            ]

            tenant = TenantConfig(
                name=tenant_name,
                ref=ref,
                databases=databases
            )
            tenant_registry.add(tenant)

        # Create the directory structure
        env_dir = os.path.join(self.temp_dir, 'test_env')
        os.makedirs(env_dir, exist_ok=True)

        # Save
        tenant_registry.save()

        # Load
        loaded_registry = TenantRegistry.load(self.temp_dir, 'test_env')

        # Verify
        self.assertEqual(len(loaded_registry), 2)

        localhost_tenant = loaded_registry['localhost']
        self.assertEqual(len(localhost_tenant.databases), 1)

        docker_tenant = loaded_registry['docker']
        self.assertEqual(len(docker_tenant.databases), 2)


if __name__ == "__main__":
    unittest.main()
