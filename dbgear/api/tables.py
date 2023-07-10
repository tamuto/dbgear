from fastapi import APIRouter
from fastapi import Request

router = APIRouter(prefix='/tables')


@router.get('/')
def get_tables(request: Request):
    return {
        ins: schema.info()
        for ins, schema in request.app.state.project.definitions.items()
    }


@router.get('/{instance}/{table}')
def get_table(instance: str, table: str, request: Request):
    schema = request.app.state.project.definitions[instance]
    return schema.get_table(table)
