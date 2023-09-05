import unittest

from unittest.mock import MagicMock

from dbgear.models.project import Project
from dbgear.api import refs

FOLDER_PATH = './etc/test'


class TestRefs(unittest.TestCase):

    def setUp(self):
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        self.request = MagicMock()
        self.request.app.state.project = proj

    def test_get_refs(self):
        result = refs.get_referencable(self.request)

        # 参照できる全てのデータ件数を確認する
        self.assertEqual(len(result.data), 6)
