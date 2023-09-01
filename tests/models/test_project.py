import unittest

from dbgear.models.project import Project

FOLDER_PATH = './etc/test'


class TestProject(unittest.TestCase):

    def test_project(self):
        proj = Project(FOLDER_PATH)
        self.assertEqual(proj.project_name, 'Test')
        self.assertEqual(len(proj.bindings.keys()), 8)
        self.assertEqual(proj.bindings['gen_uuid'].value, 'uuid')
        self.assertEqual(len(proj.rules), 3)
        self.assertEqual(proj.rules['update_date'], 'now')
        self.assertEqual(proj.deployments['localhost'], 'mysql+pymysql://root:password@denv.host?charset=utf8')

    def test_project_definitions(self):
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        self.assertEqual(len(proj.instances), 1)
        self.assertEqual(proj.instances[0], 'main')
        self.assertEqual(len(proj.schemas['main'].get_tables()), 7)

        # dictで取得できるかのテスト
        keys = [key for key, _ in proj.schemas['main'].get_tables().items()]
        self.assertEqual(len(keys), 7)

        self.assertEqual(len(proj.schemas['main'].get_table('row_table').fields), 2)
