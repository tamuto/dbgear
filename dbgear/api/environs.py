from fastapi import APIRouter
from fastapi import Request

router = APIRouter(prefix='/environs')


@router.get('/')
def get_environs(request: Request):
    return request.app.project.environs
