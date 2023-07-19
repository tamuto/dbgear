import unittest

from dbgear.models.project import Project


class TestTemplate(unittest.TestCase):

    @unittest.skip('事前にフォルダを作成する必要あり')
    def test_create_template(self):
        p = Project('dist/test')
        p.template.create_template('test', '日本語名称', ['abc', 'efg'])

    @unittest.skip('事前にフォルダを作成する必要あり')
    def test_is_exist_template(self):
        p = Project('dist/test')
        self.assertTrue(p.template.is_exist_template('test'))

    @unittest.skip('事前にフォルダを作成する必要あり')
    def test_listup_for_init(self):
        p = Project('dist/test')
        p.read_project()
        p.read_definitions()
        result = p.template.listup_for_init('test')
        print(result)

    def test_read_template_data(self):
        p = Project('dist/dbgear')
        p.read_project()
        p.read_definitions()
        result = p.template.read_template_data('test', 'facility', 'mt_position_type')
        print(result)
