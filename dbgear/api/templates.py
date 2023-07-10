from fastapi import APIRouter
from fastapi import Request

router = APIRouter(prefix='/templates')


@router.get('/')
def get_templates(request: Request):
    return request.app.project.templates
