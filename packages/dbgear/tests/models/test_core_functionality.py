import unittest
import os

from dbgear.core.models.project import Project
from dbgear.core.models.fileio import load_yaml, save_yaml
from dbgear.core.models.base import BaseSchema
from dbgear.core.models.environ import mapping

FOLDER_PATH = '../../etc/test'


class TestCoreFunctionality(unittest.TestCase):
    """Core機能の拡張テスト"""

    def test_yaml_file_operations(self):
        """YAMLファイルの読み書きテスト"""
        test_data = {'test': 'value', 'number': 42}
        temp_file = '/tmp/test_yaml.yaml'

        # 保存テスト
        save_yaml(temp_file, test_data)
        self.assertTrue(os.path.exists(temp_file))

        # 読み込みテスト
        loaded_data = load_yaml(temp_file)
        self.assertEqual(loaded_data['test'], 'value')
        self.assertEqual(loaded_data['number'], 42)

        # クリーンアップ
        os.remove(temp_file)

    def test_schema_definition_loading(self):
        """スキーマ定義の読み込みテスト"""
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        # インスタンスの確認
        self.assertIn('main', proj.schemas)
        self.assertIn('_select', proj.schemas)

        # テーブル定義の確認
        main_schema = proj.schemas['main']
        tables = main_schema.get_tables()
        self.assertGreater(len(tables), 0)

        # 特定テーブルの存在確認
        self.assertIsNotNone(main_schema.get_table('test_table'))

    def test_environment_mapping_operations(self):
        """環境マッピング操作のテスト"""
        # 環境一覧の取得
        envs = mapping.items(FOLDER_PATH)
        self.assertGreater(len(envs), 0)

        # 特定環境の取得
        test1_env = mapping.get(FOLDER_PATH, 'test1')
        self.assertEqual(test1_env.id, 'test1')
        self.assertIsNotNone(test1_env.parent)

    def test_base_schema_validation(self):
        """BaseSchemaの基本機能テスト"""
        schema = BaseSchema()

        # 基本的なメソッドが存在することを確認
        self.assertTrue(hasattr(schema, 'model_validate'))
        self.assertTrue(hasattr(schema, 'model_dump'))


if __name__ == '__main__':
    unittest.main()
