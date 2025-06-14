import unittest

from dbgear_web.api import dtos
from dbgear.core.models.schema import Table
from dbgear.core.models import const


class TestDTOs(unittest.TestCase):

    def test_mapping(self):
        data = dtos.convert_to_mapping('test', dtos.NewMapping(
            group='Test',
            base=None,
            name='abc',
            deployment=False
        ))
        self.assertEqual(data.id, 'test')
        self.assertEqual(data.name, 'abc')
        self.assertEqual(data.description, '')
        self.assertEqual(data.instances, [])
        self.assertEqual(data.deployment, False)

    def test_data_model(self):
        data = dtos.convert_to_data_model(dtos.NewDataModel(
            description='abc',
            layout='test',
            settings={},
            sync_mode=const.SYNC_MODE_DROP_CREATE,
            value='id',
            caption='name'
        ))
        self.assertEqual(data.id, '')
        self.assertEqual(data.instance, '')
        self.assertEqual(data.table_name, '')
        self.assertEqual(data.description, 'abc')
        self.assertEqual(data.layout, 'test')
        self.assertEqual(data.settings, {})

    def test_filename(self):
        data = dtos.convert_to_data_filename(
            instance='test',
            tbl=Table(
                instance='test',
                table_name='abc',
                display_name='123'
            )
        )
        self.assertEqual(data.instance, 'test')
        self.assertEqual(data.table_name, 'abc')
        self.assertEqual(data.display_name, '123')
