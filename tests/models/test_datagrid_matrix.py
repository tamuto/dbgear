import unittest

from dbgear.models.project import Project
from dbgear.models.environ import mapping
from dbgear.models.environ import entity
from dbgear.models.datagrid import grid
from dbgear.models.datagrid.data import DataModel
from dbgear.models.fileio import load_model
from dbgear.models.fileio import get_data_model_name
from dbgear.models import const

FOLDER_PATH = './etc/test'


class TestDataGrid(unittest.TestCase):

    def test_tbl_matrix(self):
        # マトリックステーブル
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test2')

        dm, _, info = entity.get(proj, map, 'main', 'tbl_matrix')

        self.assertEqual(dm.layout, const.LAYOUT_MATRIX)
        self.assertEqual(len(info.grid_columns), 5)
        self.assertEqual(info.grid_columns[1].field, '3f2a4961-4363-4c9e-aba1-8a91f6909be7_value')
        self.assertEqual(info.grid_columns[1].header_name, 'AAA(値)')
        self.assertEqual(len(info.grid_columns[1].items), 2)
        self.assertEqual(len(info.grid_rows), 3)

    def test_parse(self):
        proj = Project(FOLDER_PATH)
        proj.read_definitions()

        map = mapping.get(proj.folder, 'test2')
        ins = 'main'
        tbl = 'tbl_matrix'

        dm = load_model(
            get_data_model_name(proj.folder, map.id, ins, tbl),
            DataModel,
            id=map.id,
            instance=ins,
            table_name=tbl,
        )
        table = proj.schemas[ins].get_table(tbl)

        rows = [
            {
                'row_id': 'c744603c-635e-4af8-a48e-b85418e1f569',
                '3f2a4961-4363-4c9e-aba1-8a91f6909be7_value': 'Test1-AAA',
                '444307b2-b838-4cb1-908f-9f41e6605f29_value': '',
                '84d85612-e010-4548-bcd6-0d4686f34570_value': 'Test1-CCC',
                'e6ac8323-fa26-4107-be08-6a42c5293937_value': 'Test1-DDD',
                'id': 'f36ee881-905b-4ee3-aac8-2bfaf6b9df49'
            },
            {
                'row_id': 'c99032cf-3e34-492b-bce9-6716b4b93540',
                '3f2a4961-4363-4c9e-aba1-8a91f6909be7_value': '',
                '444307b2-b838-4cb1-908f-9f41e6605f29_value': '',
                '84d85612-e010-4548-bcd6-0d4686f34570_value': 'Test2-CCC',
                'e6ac8323-fa26-4107-be08-6a42c5293937_value': 'Test2-DDD',
                'id': '00b1343a-66d2-4fd2-9985-f3a22c06d939'
            },
            {
                'row_id': 'db801745-50bd-4084-83fa-c3feec593cd9',
                '3f2a4961-4363-4c9e-aba1-8a91f6909be7_value': 'Test3-AAA',
                '444307b2-b838-4cb1-908f-9f41e6605f29_value': '',
                '84d85612-e010-4548-bcd6-0d4686f34570_value': 'Test3-CCC',
                'e6ac8323-fa26-4107-be08-6a42c5293937_value': '',
                'id': '0814473d-004d-4e80-8def-a35ebb971032'
            },
            {
                'row_id': '123',
                '3f2a4961-4363-4c9e-aba1-8a91f6909be7_value': '',
                '444307b2-b838-4cb1-908f-9f41e6605f29_value': '',
                '84d85612-e010-4548-bcd6-0d4686f34570_value': '',
                'e6ac8323-fa26-4107-be08-6a42c5293937_value': '',
                'id': '5e626150-0ff6-4d6b-8dd8-347359e741f5'
            }
        ]

        data = grid.parse(proj, map, dm, table, rows)
        self.assertEqual(len(data), 16)
        self.assertEqual(data[0]['value'], 'Test1-AAA')
