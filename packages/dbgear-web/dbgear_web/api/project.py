from fastapi import APIRouter
from fastapi import Request

from ..shared.helpers import get_project
from ..shared.dtos import Result

router = APIRouter()


@router.get('/project', response_model=Result)
def get_project_info(request: Request) -> Result:
    return Result(status='OK', data=get_project(request))
