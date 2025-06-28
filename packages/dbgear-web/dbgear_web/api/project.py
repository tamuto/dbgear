import os
from fastapi import APIRouter
from fastapi import Request

from ..shared.helpers import get_project
from ..shared.dtos import Result
from ..shared.dtos import ProjectInfo

router = APIRouter()


@router.get('/project', response_model=Result)
def get_project_info(request: Request) -> Result:
    proj = get_project(request)
    api_key = os.environ.get('API_KEY', None)

    info = ProjectInfo(
        project_name=proj.project_name,
        description=proj.description,
        bindings=proj.bindings,
        rules=proj.rules,
        instances=proj.instances,
        api_key=api_key
    )
    return Result(status='OK', data=info)
