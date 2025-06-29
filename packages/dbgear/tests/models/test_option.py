import unittest
import tempfile
import os
import yaml

from dbgear.models.option import Options
from dbgear.models.project import Project
from dbgear.models.environ import Environ, EnvironManager


class TestDBGearOptions(unittest.TestCase):
    """Test DBGearOptions model"""

    def test_default_options(self):
        """Test default option values"""
        options = Options()

        # Test default values
        self.assertTrue(options.create_foreign_key_constraints)

    def test_custom_options(self):
        """Test custom option values"""
        options = Options(create_foreign_key_constraints=False)

        # Test custom values
        self.assertFalse(options.create_foreign_key_constraints)

    def test_options_serialization(self):
        """Test options serialization/deserialization"""
        options = Options(create_foreign_key_constraints=False)

        # Test serialization
        data = options.model_dump()
        self.assertEqual(data['create_foreign_key_constraints'], False)

        # Test deserialization
        new_options = Options(**data)
        self.assertFalse(new_options.create_foreign_key_constraints)


class TestProjectWithOptions(unittest.TestCase):
    """Test Project model with options"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_project_default_options(self):
        """Test Project with default options"""
        project = Project(
            folder=self.temp_dir,
            project_name='test_project',
            description='Test project'
        )

        # Test default options
        self.assertIsInstance(project.options, Options)
        self.assertTrue(project.options.create_foreign_key_constraints)

    def test_project_custom_options(self):
        """Test Project with custom options"""
        custom_options = Options(create_foreign_key_constraints=False)
        project = Project(
            folder=self.temp_dir,
            project_name='test_project',
            description='Test project',
            options=custom_options
        )

        # Test custom options
        self.assertFalse(project.options.create_foreign_key_constraints)

    def test_project_save_load_with_options(self):
        """Test Project save/load with options"""
        # Create project with custom options
        custom_options = Options(create_foreign_key_constraints=False)
        original_project = Project(
            folder=self.temp_dir,
            project_name='test_project',
            description='Test project with options',
            options=custom_options
        )

        # Save project
        original_project.save()

        # Load project
        loaded_project = Project.load(self.temp_dir)

        # Verify options are preserved
        self.assertEqual(loaded_project.project_name, 'test_project')
        self.assertEqual(loaded_project.description, 'Test project with options')
        self.assertFalse(loaded_project.options.create_foreign_key_constraints)

    def test_project_yaml_format(self):
        """Test Project YAML format includes options"""
        custom_options = Options(create_foreign_key_constraints=False)
        project = Project(
            folder=self.temp_dir,
            project_name='test_project',
            description='Test project',
            options=custom_options
        )

        # Save and check YAML content
        project.save()

        with open(os.path.join(self.temp_dir, 'project.yaml'), 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)

        # Verify options in YAML
        self.assertIn('options', yaml_data)
        # When value is False (non-default), it should be included (as camelCase due to alias)
        self.assertIn('createForeignKeyConstraints', yaml_data['options'])
        self.assertEqual(yaml_data['options']['createForeignKeyConstraints'], False)


class TestEnvironWithOptions(unittest.TestCase):
    """Test Environ model with options"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_environ_default_options(self):
        """Test Environ with default options (None)"""
        environ = Environ(
            folder=self.temp_dir,
            name='test_env',
            description='Test environment'
        )

        # Test default options (should be None)
        self.assertIsNone(environ.options)

    def test_environ_custom_options(self):
        """Test Environ with custom options"""
        custom_options = Options(create_foreign_key_constraints=False)
        environ = Environ(
            folder=self.temp_dir,
            name='test_env',
            description='Test environment',
            options=custom_options
        )

        # Test custom options
        self.assertFalse(environ.options.create_foreign_key_constraints)

    def test_environ_save_load_with_options(self):
        """Test Environ save/load with options via EnvironManager"""
        # Create environ with custom options
        custom_options = Options(create_foreign_key_constraints=False)
        environ = Environ(
            folder=self.temp_dir,
            name='test_env',
            description='Test environment with options',
            options=custom_options
        )

        # Save environ via EnvironManager
        environ_manager = EnvironManager(self.temp_dir)
        environ_manager.add(environ)

        # Load environ
        loaded_environ = environ_manager['test_env']

        # Verify options are preserved
        self.assertEqual(loaded_environ.name, 'test_env')
        self.assertEqual(loaded_environ.description, 'Test environment with options')
        self.assertFalse(loaded_environ.options.create_foreign_key_constraints)

    def test_environ_yaml_format(self):
        """Test Environ YAML format includes options"""
        custom_options = Options(create_foreign_key_constraints=False)
        environ = Environ(
            folder=self.temp_dir,
            name='test_env',
            description='Test environment',
            options=custom_options
        )

        # Save via EnvironManager
        environ_manager = EnvironManager(self.temp_dir)
        environ_manager.add(environ)

        # Check YAML content
        environ_file = os.path.join(self.temp_dir, 'test_env', 'environ.yaml')
        with open(environ_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)

        # Verify options in YAML
        self.assertIn('options', yaml_data)
        # When value is False (non-default), it should be included (as camelCase due to alias)
        self.assertIn('createForeignKeyConstraints', yaml_data['options'])
        self.assertEqual(yaml_data['options']['createForeignKeyConstraints'], False)


if __name__ == "__main__":
    unittest.main()
