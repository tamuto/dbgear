from fastapi import APIRouter
from fastapi import Request
from fastapi import Body

from ..models.project import project
from ..models.environ import mapping
from ..models.environ import entity
from ..models.environ import import_sql

from .dtos import Result
from .dtos import Data
from .dtos import NewMapping
from .dtos import NewDataModel
from .dtos import ImportSQL
from .dtos import MappingTree
from .dtos import convert_to_data_filename
from .dtos import convert_to_mapping
from .dtos import convert_to_data_model

router = APIRouter(prefix='/environs')


@router.get('')
def get_mappings(request: Request):
    proj = project(request)
    maps = mapping.items(proj.folder)

    groupTree = {}
    for map in maps:
        if map.group not in groupTree:
            groupTree[map.group] = MappingTree(name=map.group, children=[])
        groupTree[map.group].children.append(map)

    return Result(data=[*groupTree.values()])


@router.post('/{id}')
def create_mapping(id: str, data: NewMapping, request: Request) -> Result:
    proj = project(request)
    if mapping.is_exist(proj.folder, id):
        return Result(
            status='ERROR',
            message='ERROR_EXIST_MAPPING'
        )
    mapping.save(proj.folder, id, convert_to_mapping(id, data))
    return Result()


@router.get('/{id}/tables')
def get_tables(id: str, request: Request):
    '''
    既に存在するテーブル一覧。
    '''
    proj = project(request)
    tables = [
        convert_to_data_filename(
            ins,
            tbl,
            entity.get_description(proj, id, ins, tbl.table_name)
        )
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
def get_table(id: str, instance: str, table: str, request: Request, segment: str | None = None):
    proj = project(request)
    map = mapping.get(proj.folder, id)
    dm, tbl, info = entity.get(proj, map, instance, table, segment)
    data = Data(
        model=dm,
        info=info,
        table=tbl
    )
    return Result(data=data)


@router.get('/{id}/tables/{instance}/{table}/row')
def get_row(id: str, instance: str, table: str, request: Request):
    proj = project(request)
    map = mapping.get(proj.folder, id)
    row = entity.get_row(proj, map, instance, table)
    return Result(data=row)


@router.post('/{id}/tables/{instance}/{table}')
def create_data_model(id: str, instance: str, table: str, data: NewDataModel, request: Request):
    proj = project(request)
    map = mapping.get(proj.folder, id)
    entity.save(proj, map, instance, table, convert_to_data_model(data))
    return Result()


@router.put('/{id}/tables/{instance}/{table}')
def update_data(id: str, instance: str, table: str, request: Request, body=Body(...), segment: str | None = None):
    proj = project(request)
    map = mapping.get(proj.folder, id)
    entity.save_data(proj, map, instance, table, segment, body)
    return Result()


@router.post('/{id}/tables/{instance}/{table}/import')
def import_data(id: str, instance: str, table: str, imp: ImportSQL, request: Request, segment: str | None = None):
    proj = project(request)
    map = mapping.get(proj.folder, id)
    import_sql.execute(proj, map, instance, table, segment, imp.host, imp.sql)
    return Result()
