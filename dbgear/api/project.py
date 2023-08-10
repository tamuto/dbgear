from fastapi import APIRouter
from fastapi import Request

from ..models.project import project
from ..models.environ import mapping as template_mapping
from .dtos import Result
from .dtos import ProjectInfo

router = APIRouter(prefix='/project')


@router.get('/')
def get_project_info(request: Request) -> Result:
    proj = project(request)

    templates = template_mapping.items(proj.folder)
    environs = []
    info = ProjectInfo(
        project_name=proj.project_name,
        templates=templates,
        environs=environs,
        instances=proj.instances,
        column_settings=proj.bindings,
        rules=proj.rules
    )
    return Result(data=info)
