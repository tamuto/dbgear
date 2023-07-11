from fastapi import APIRouter
from fastapi import Request

from ..models.result import Result
from ..models.templates import NewTemplate

router = APIRouter(prefix='/templates')


@router.get('/')
def get_templates(request: Request):
    return request.app.state.project.templates


@router.post('/')
def create_template(data: NewTemplate, request: Request):
    if request.app.state.project.is_exist_template(data.id):
        return Result(
            status='ERROR',
            message='ERROR_EXIST_TEMPLATE_FOLDER'
        )
    request.app.state.project.create_template(**data)
    return Result(status='OK')
