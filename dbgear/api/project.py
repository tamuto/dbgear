from fastapi import APIRouter
from fastapi import Request

from ..models.project import project
from .dtos import Result
from .dtos import ProjectInfo

router = APIRouter(prefix='/project')


@router.get('/')
def get_project_info(request: Request) -> Result:
    proj = project(request)

    info = ProjectInfo(
        project_name=proj.project_name,
        bindings=proj.bindings,
        rules=proj.rules
    )
    return Result(data=info)
