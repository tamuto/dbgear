import unittest

from dbgear.project import Project


class TestProject(unittest.TestCase):

    @unittest.skip('事前にフォルダを作成する必要あり')
    def test_create_template(self):
        p = Project('dist/test')
        p.create_template('test', '日本語名称', ['abc', 'efg'])

    @unittest.skip('事前にフォルダを作成する必要あり')
    def test_is_exist_template(self):
        p = Project('dist/test')
        self.assertTrue(p.is_exist_template('test'))
