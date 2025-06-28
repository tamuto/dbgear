import re
import os
from glob import glob

from fastapi import APIRouter
from fastapi import Request

from ..shared.helpers import get_project
from dbgear.models.environ import EnvironManager
from ..shared.dtos import Result
from ..shared.dtos import DataFilename

router = APIRouter()


@router.get('/refs')
def get_referencable(request: Request) -> Result:
    proj = get_project(request)

    # データを横断して検索して一覧を生成する
    data = []
    
    # 環境マネージャーを使用してマッピングを取得
    env_manager = EnvironManager(proj.folder)
    
    for environ in env_manager:
        for mapping in environ.mappings:
            # 環境内のデータファイルを検索
            data_path = f"{proj.folder}/{environ.name}/{mapping.name}"
            if os.path.exists(data_path):
                for dat_file in glob(f"{data_path}/*.dat"):
                    name = os.path.basename(dat_file)
                    if '#' in name:
                        (ins, tbl, _, _) = re.split('[.@#]', name)
                    else:
                        (ins, tbl, _) = re.split('[.@]', name)
                    
                    # スキーマからテーブル情報を取得
                    if ins in proj.schemas and tbl in proj.schemas[ins].tables:
                        table = proj.schemas[ins].tables[tbl]
                        data.append(DataFilename(
                            id=mapping.name,
                            instance=ins,
                            table_name=tbl,
                            display_name=table.display_name,
                            description=None,
                            id_name=mapping.name
                        ))

    return Result(data=data)
