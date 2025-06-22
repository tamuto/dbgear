import unittest
import os

from dbgear.core.models.project import Project


class TestProject(unittest.TestCase):

    def test_save(self):
        project = Project(
            folder='.',
            project_name="Test Project",
            description="A test project")
        project.save()
        os.remove('./project.yaml')


if __name__ == "__main__":
    unittest.main()
