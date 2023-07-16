from fastapi import APIRouter
from fastapi import Request

from ..models.proxy import APIProxy
from ..models.request import NewTemplate
from ..models.request import NewTemplateData
from ..models.response import Result

router = APIRouter(prefix='/templates')


@router.post('/')
def create_template(data: NewTemplate, request: Request):
    api = APIProxy(request.app)
    if api.is_exist_template(data.id):
        return Result(
            status='ERROR',
            message='ERROR_EXIST_TEMPLATE_FOLDER'
        )
    api.create_template(**data.model_dump())
    return Result(status='OK')


@router.get('/{id}/init')
def get_init_list(id: str, request: Request):
    api = APIProxy(request.app)
    return api.listup_for_init(id)


@router.get('/{id}')
def get_data_list(id: str, request: Request):
    api = APIProxy(request.app)
    return api.listup_data(id)


@router.post('/{id}')
def create_data(id: str, data: NewTemplateData, request: Request):
    api = APIProxy(request.app)
    if api.is_exist_data(id, data.instance, data.table_name):
        return Result(
            status='ERROR'
        )
    api.create_template_data(id=id, **data.model_dump())
    return Result(status='OK')


@router.get('/{id}/{instance}/{table}')
def get_data(id: str, instance: str, table: str, request: Request):
    api = APIProxy(request.app)
    return api.read_template_data(id, instance, table)
