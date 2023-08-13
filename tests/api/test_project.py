import unittest

from unittest.mock import MagicMock

from dbgear.models.project import Project
from dbgear.api import project


FOLDER_PATH = './dist/test'


class TestProject(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)

        self.request = MagicMock()
        self.request.app.state.project = proj

    def test_get_project(self):
        result = project.get_project_info(self.request)
        self.assertEqual(result.status, 'OK')
