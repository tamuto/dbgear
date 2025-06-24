import unittest
import tempfile
import os
import yaml

from dbgear.models.project import Project


class TestProject(unittest.TestCase):
    """Test Project YAML file I/O operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_yaml_path = os.path.join(self.temp_dir, 'project.yaml')

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_project_save_and_load(self):
        """Test Project save and load operations"""
        # Create test project
        project = Project(
            folder=self.temp_dir,
            project_name="Test Project",
            description="A test project for testing"
        )

        # Test save
        project.save()
        self.assertTrue(os.path.exists(self.project_yaml_path))

        # Verify saved content
        with open(self.project_yaml_path, 'r', encoding='utf-8') as f:
            saved_data = yaml.safe_load(f)

        # Check both possible field names (camelCase from alias or original)
        project_name = saved_data.get('projectName') or saved_data.get('project_name')
        self.assertEqual(project_name, 'Test Project')
        self.assertEqual(saved_data['description'], 'A test project for testing')

        # Test load
        loaded_project = Project.load(self.temp_dir)
        self.assertEqual(loaded_project.project_name, 'Test Project')
        self.assertEqual(loaded_project.description, 'A test project for testing')
        self.assertEqual(loaded_project.folder, self.temp_dir)

    def test_project_load_from_existing_yaml(self):
        """Test loading Project from existing YAML file"""
        # Create test YAML data
        project_data = {
            'projectName': 'Existing Project',
            'description': 'Project loaded from YAML'
        }

        # Write test data
        with open(self.project_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(project_data, f, allow_unicode=True)

        # Test load
        project = Project.load(self.temp_dir)
        self.assertEqual(project.project_name, 'Existing Project')
        self.assertEqual(project.description, 'Project loaded from YAML')

    def test_project_roundtrip(self):
        """Test Project save/load roundtrip"""
        # Original project
        original = Project(
            folder=self.temp_dir,
            project_name="Roundtrip Test",
            description="Testing save/load roundtrip"
        )

        # Save
        original.save()

        # Load
        loaded = Project.load(self.temp_dir)

        # Verify
        self.assertEqual(original.project_name, loaded.project_name)
        self.assertEqual(original.description, loaded.description)


if __name__ == "__main__":
    unittest.main()
