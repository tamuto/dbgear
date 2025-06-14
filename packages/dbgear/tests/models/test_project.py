import unittest

from dbgear.core.models.project import Project

FOLDER_PATH = '../../etc/test'


class TestProject(unittest.TestCase):

    def test_project(self):
        proj = Project(FOLDER_PATH)
        self.assertEqual(proj.project_name, 'Test')
        self.assertEqual(len(proj.bindings.keys()), 8)
        self.assertEqual(proj.bindings['gen_uuid'].value, 'uuid')
        self.assertEqual(len(proj.rules), 3)
        self.assertEqual(proj.rules['update_date'], 'now')
        self.assertEqual(proj.deployments['localhost'], 'mysql+pymysql://root:password@host.docker.internal?charset=utf8mb4')

    def test_project_definitions(self):
        proj = Project(FOLDER_PATH)
        proj.read_definitions()
        self.assertEqual(len(proj.instances), 2)
        self.assertEqual(proj.instances[0], 'main')
        self.assertEqual(len(proj.schemas['main'].get_tables()), 8)

        # dictで取得できるかのテスト
        keys = [key for key, _ in proj.schemas['main'].get_tables().items()]
        self.assertEqual(len(keys), 8)

        self.assertEqual(len(proj.schemas['main'].get_table('row_table').fields), 2)

    def test_project_configuration_validation(self):
        """プロジェクト設定の検証"""
        proj = Project(FOLDER_PATH)
        
        # プロジェクト名の検証
        self.assertEqual(proj.project_name, 'Test')
        
        # bindings設定の検証
        self.assertIn('uuid', proj.bindings)
        self.assertIn('now', proj.bindings)
        self.assertEqual(proj.bindings['gen_uuid'].value, 'uuid')
        
        # deployments設定の検証
        self.assertIn('localhost', proj.deployments)
        self.assertTrue(proj.deployments['localhost'].startswith('mysql+pymysql://'))

    def test_project_loading_error_handling(self):
        """存在しないプロジェクトファイルの読み込みエラーハンドリング"""
        with self.assertRaises(FileNotFoundError):
            Project('./nonexistent')


if __name__ == '__main__':
    unittest.main()