from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException

from dbgear.models.mapping import Mapping

from ..shared.dtos import Result, CreateMappingRequest, UpdateMappingRequest
from ..shared.helpers import get_project

router = APIRouter()


@router.get('/environments/{env_name}/mappings')
def get_mappings(env_name: str, request: Request):
    """Get all mappings in an environment"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        return Result(data=list(project.envs[env_name].mappings))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}')
def get_mapping(env_name: str, mapping_name: str, request: Request):
    """Get a specific mapping"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return Result(data=project.envs[env_name].mappings[mapping_name])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments/{env_name}/mappings')
def create_mapping(env_name: str, data: CreateMappingRequest, request: Request):
    """Create a new mapping in an environment"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if data.name in project.envs[env_name].mappings:
            raise HTTPException(status_code=409, detail="Mapping already exists")

        mapping = Mapping(
            folder=project.folder,
            environ=env_name,
            name=data.name,
            description=data.description,
            schemas=data.schemas or [],
            shared=data.shared,
            deploy=data.deploy,
        )

        project.envs[env_name].mappings.add(mapping)
        return Result(data=mapping)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/environments/{env_name}/mappings/{mapping_name}')
def update_mapping(env_name: str, mapping_name: str, data: UpdateMappingRequest, request: Request):
    """Update an existing mapping"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        mapping = project.envs[env_name].mappings[mapping_name]
        mapping.description = data.description
        mapping.schemas = data.schemas
        mapping.shared = data.shared
        mapping.deploy = data.deploy

        mapping.save()
        return Result(data=mapping)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/environments/{env_name}/mappings/{mapping_name}')
def delete_mapping(env_name: str, mapping_name: str, request: Request):
    """Delete a mapping"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        project.envs[env_name].mappings.remove(mapping_name)
        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels')
def get_mapping_datamodels(env_name: str, mapping_name: str, request: Request):
    """Get data models associated with a mapping"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        return Result(data=project.envs[env_name].mappings[mapping_name].datamodels)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
