from fastapi import APIRouter
from fastapi import Request
from fastapi import Body

from ..models.project import project
from ..models.environ import mapping
from ..models.environ import entity

from .dtos import Result
from .dtos import Data
from .dtos import NewMapping
from .dtos import NewDataModel
from .dtos import convert_to_data_filename
from .dtos import convert_to_mapping
from .dtos import convert_to_data_model

router = APIRouter(prefix='/environs')


@router.post('/{id}')
def create_mapping(id: str, data: NewMapping, request: Request) -> Result:
    proj = project(request)
    if mapping.is_exist(proj.folder, id):
        return Result(
            status='ERROR',
            message='ERROR_EXIST_MAPPING'
        )
    mapping.save(proj.folder, id, convert_to_mapping(data))
    return Result()


@router.get('/{id}/tables')
def get_tables(id: str, request: Request):
    '''
    既に存在するテーブル一覧。
    '''
    proj = project(request)
    tables = [
        convert_to_data_filename(ins, tbl)
        for ins, tbl in entity.items(proj.schemas, proj.folder, id)
    ]
    return Result(data=tables)


@router.get('/{id}/init')
def get_not_exist_tables(id: str, request: Request):
    '''
    新規作成時のテーブル一覧。既に存在するものは除く
    '''
    proj = project(request)
    tables = [
        convert_to_data_filename(ins, tbl)
        for ins, tbl in entity.items(proj.schemas, proj.folder, id, exist=False)
    ]
    return Result(data=tables)


@router.get('/{id}/tables/{instance}/{table}')
def get_table(id: str, instance: str, table: str, request: Request):
    proj = project(request)
    dm, tbl, info = entity.get(proj.bindings, proj.schemas, proj.folder, id, instance, table)
    data = Data(
        model=dm,
        info=info,
        table=tbl
    )
    return Result(data=data)


@router.post('/{id}/tables/{instance}/{table}')
def create_data_model(id: str, instance: str, table: str, data: NewDataModel, request: Request):
    proj = project(request)
    entity.save(proj.folder, id, instance, table, convert_to_data_model(data))
    return Result()


@router.put('/{id}/tables/{instance}/{table}')
def update_data(id: str, instance: str, table: str, request: Request, body=Body(...)):
    proj = project(request)
    entity.save_data(proj.schemas, proj.folder, id, instance, table, body)
    return Result()



# @router.get('/{id}/{instance}/{table}/new_row')
# def get_new_data_row(id: str, instance: str, table: str, request: Request):
#     api = APIProxy(request.app)
#     return api.build_new_data_row(id, instance, table)
