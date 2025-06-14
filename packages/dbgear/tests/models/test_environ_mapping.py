import unittest

from dbgear.core.models.environ.data import Mapping
from dbgear.core.models.environ import mapping

FOLDER_PATH = '../../etc/test'


class TestEnviron(unittest.TestCase):

    def test_mapping_items(self):
        items = mapping.items(FOLDER_PATH)
        self.assertEqual(len(items), 2)
        self.assertTrue(any(item.id == 'test1' for item in items))
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


if __name__ == '__main__':
    unittest.main()