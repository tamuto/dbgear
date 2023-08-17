from fastapi import APIRouter
from fastapi import Request

from ..models.project import project
from .dtos import Result
from .dtos import convert_to_data_filename

router = APIRouter(prefix='/tables')


@router.get('')
def get_tables(request: Request) -> Result:
    proj = project(request)
    tables = {
        ins: sorted([
            convert_to_data_filename(ins, tbl)
            for tbl in schema.get_tables().values()
        ], key=lambda x: x.table_name)
        for ins, schema in proj.schemas.items()
    }
    return Result(data=tables)


@router.get('/{instance}/{table}')
def get_table(instance: str, table: str, request: Request) -> Result:
    proj = project(request)
    schema = proj.schemas[instance]
    table = schema.get_table(table)
    return Result(data=table)
