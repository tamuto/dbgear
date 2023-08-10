import unittest

from dbgear.models.environ.data import Mapping
from dbgear.models.environ import mapping

FOLDER_PATH = './etc/test'


class TestEnviron(unittest.TestCase):

    def test_mapping_items(self):
        items = mapping.items(FOLDER_PATH)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].id, 'test1')
        self.assertEqual(items[0].description, '')
        self.assertEqual(items[1].id, 'test2')
        self.assertEqual(items[1].description, 'ABC')

    def test_mapping_get(self):
        item = mapping.get(FOLDER_PATH, 'test1')
        self.assertEqual(item.id, 'test1')
        self.assertEqual(item.description, '')

    def test_mapping_save(self):
        mapping.save(FOLDER_PATH, 'test3', Mapping(
            id='Test3',
            name='AAAABBBBCCCC',
            base=None,
        ))
        item = mapping.get(FOLDER_PATH, 'test3')
        self.assertEqual(item.name, 'AAAABBBBCCCC')
        mapping.delete(FOLDER_PATH, 'test3')
