import unittest
import tempfile
import os

from dbgear.models.tenant import TenantRegistry, TenantConfig, DatabaseInfo


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
            database='testdb',
            description='Test database',
            active=True
        )

        tenant_config = TenantConfig(
            name='localhost',
            ref='base',
            databases=[db_info]
        )

        tenant_registry.append(tenant_config)

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
        self.assertEqual(loaded_db.database, 'testdb')
        self.assertTrue(loaded_db.active)

    def test_tenant_roundtrip(self):
        """Test TenantRegistry save/load roundtrip"""
        # Create complex tenant registry
        tenant_registry = TenantRegistry(folder=self.temp_dir, name='test_env')

        # Multiple tenants with different configurations
        tenants_data = [
            ('localhost', 'local_base', [
                ('local_main', 'Local main DB', True)
            ]),
            ('docker', 'docker_base', [
                ('docker_main', 'Docker main DB', True),
                ('docker_test', 'Docker test DB', False)
            ])
        ]

        for tenant_name, ref, dbs in tenants_data:
            databases = [
                DatabaseInfo(database=db, description=desc, active=active)
                for db, desc, active in dbs
            ]

            tenant = TenantConfig(
                name=tenant_name,
                ref=ref,
                databases=databases
            )
            tenant_registry.append(tenant)

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
