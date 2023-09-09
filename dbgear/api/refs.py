import re
from glob import glob

from fastapi import APIRouter
from fastapi import Request

from ..models.project import project
from ..models.environ.data import Mapping
from ..models.fileio import load_model
from ..models.fileio import get_mapping_name
from ..models.fileio import get_environ_name
from .dtos import Result
from .dtos import DataFilename

router = APIRouter(prefix='/refs')


@router.get('')
def get_referencable(request: Request) -> Result:
    proj = project(request)

    # データを横断して検索して一覧を生成する
    data = []
    for tmpl in glob(get_mapping_name(proj.folder, '**')):
        id = tmpl.split('/')[-2]
        map = load_model(tmpl, Mapping, id=id)
        for dat in glob(get_environ_name(proj.folder, id) + '/*.dat'):
            name = dat.split('/')[-1]
            if '#' in name:
                (ins, tbl, _, _) = re.split('[.@#]', name)
            else:
                (ins, tbl, _) = re.split('[.@]', name)
            table = proj.schemas[ins].get_table(tbl)
            data.append(DataFilename(
                id=id,
                instance=ins,
                table_name=tbl,
                display_name=table.display_name,
                description=None,
                id_name=map.name
            ))

    return Result(data=data)
