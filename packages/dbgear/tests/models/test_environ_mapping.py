import unittest
import os
import shutil

from dbgear.core.models.environ.data import Mapping
from dbgear.core.models.environ import mapping

FOLDER_PATH = '../../etc/test'


class TestEnviron(unittest.TestCase):

    def setUp(self):
        """Clean up any test3 directory before each test"""
        test3_path = os.path.join(FOLDER_PATH, 'test3')
        if os.path.exists(test3_path):
            shutil.rmtree(test3_path)

    def tearDown(self):
        """Clean up any test3 directory after each test"""
        test3_path = os.path.join(FOLDER_PATH, 'test3')
        if os.path.exists(test3_path):
            shutil.rmtree(test3_path)

    def test_mapping_items(self):
        items = mapping.items(FOLDER_PATH)
        self.assertEqual(len(items), 2)
        self.assertTrue(any(item.id == 'test1' for item in items))
        self.assertTrue(any(item.id == 'base' for item in items))
        self.assertIsInstance(items[0].description, str)
        # test1とbaseの2つの環境が存在することを確認

    def test_mapping_get(self):
        item = mapping.get(FOLDER_PATH, 'test1')
        self.assertEqual(item.id, 'test1')
        self.assertEqual(item.name, 'テスト1')
        self.assertEqual(item.parent.id, 'base')

    def test_mapping_save(self):
        mapping.save(FOLDER_PATH, 'test3', Mapping(
            id='Test3',
            group='Test',
            base=None,
            name='テスト3',
            description='Test 3',
            deployment=False
        ))

        # Verify the mapping was saved correctly
        saved_mapping = mapping.get(FOLDER_PATH, 'test3')
        self.assertEqual(saved_mapping.id, 'test3')
        self.assertEqual(saved_mapping.name, 'テスト3')

        # Clean up after test
        test3_path = os.path.join(FOLDER_PATH, 'test3')
        if os.path.exists(test3_path):
            shutil.rmtree(test3_path)


if __name__ == '__main__':
    unittest.main()
