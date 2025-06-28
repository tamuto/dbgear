from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException

from dbgear.models.environ import Environ

from ..shared.dtos import Result
from ..shared.dtos import CreateEnvironmentRequest
from ..shared.dtos import UpdateEnvironmentRequest
from ..shared.helpers import get_project

router = APIRouter()


@router.get('/environments')
def get_environments(request: Request):
    """Get all environments"""
    try:
        project = get_project(request)
        return Result(data=list(project.envs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}')
def get_environment(env_name: str, request: Request):
    """Get a specific environment"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        return Result(data=project.envs[env_name])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments')
def create_environment(data: CreateEnvironmentRequest, request: Request):
    """Create a new environment"""
    try:
        project = get_project(request)
        if data.name in project.envs:
            raise HTTPException(status_code=400, detail="Environment already exists")
        # Create environment
        environ = Environ(
            folder=project.folder,
            name=data.name,
            description=data.description,
            options=data.options or {},
        )
        project.envs.add(environ)
        return Result(data=environ)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/environments/{env_name}')
def update_environment(env_name: str, data: UpdateEnvironmentRequest, request: Request):
    """Update an existing environment"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        environ = project.envs[env_name]
        environ.description = data.description
        environ.options = data.options or {}
        # environ.save()
        return Result(data=environ)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/environments/{env_name}')
def delete_environment(env_name: str, request: Request):
    """Delete an environment"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        project.envs.remove(env_name)
        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/schemas')
def get_environment_schemas(env_name: str, request: Request):
    """Get environment-specific schemas"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        return Result(data=list(project.envs[env_name].schemas))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
