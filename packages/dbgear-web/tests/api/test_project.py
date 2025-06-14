import unittest

from unittest.mock import MagicMock

from dbgear.core.models.project import Project
from dbgear_web.api import project


FOLDER_PATH = '../../etc/test'


class TestProject(unittest.TestCase):

    def setUp(self) -> None:
        proj = Project(FOLDER_PATH)

        self.request = MagicMock()
        self.request.app.state.project = proj

    def test_get_project(self):
        result = project.get_project_info(self.request)
        self.assertEqual(result.status, 'OK')
