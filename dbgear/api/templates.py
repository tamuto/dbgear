from fastapi import APIRouter
from fastapi import Request

from ..models.proxy import APIProxy
from ..models.request import NewTemplate
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
    api.create_template(**data)
    return Result(status='OK')


@router.get('/{id}/init')
def get_init_list(id: str, request: Request):
    api = APIProxy(request.app)
    return api.listup_for_init(id)
