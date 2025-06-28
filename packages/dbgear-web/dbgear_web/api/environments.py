from fastapi import APIRouter, Request, HTTPException
from dbgear.models.environ import Environ, EnvironManager
from ..shared.dtos import Result, CreateEnvironmentRequest, UpdateEnvironmentRequest
from ..shared.helpers import get_project


router = APIRouter()


def get_environ_manager(request: Request) -> EnvironManager:
    """Get EnvironManager from project"""
    project = get_project(request)
    return EnvironManager(project.folder)


@router.get('/environments')
def get_environments(request: Request):
    """Get all environments"""
    try:
        manager = get_environ_manager(request)
        return Result(data=list(manager))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}')
def get_environment(env_name: str, request: Request):
    """Get a specific environment"""
    try:
        manager = get_environ_manager(request)

        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        environ = manager[env_name]
        return Result(data=environ)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments')
def create_environment(data: CreateEnvironmentRequest, request: Request):
    """Create a new environment"""
    try:
        manager = get_environ_manager(request)

        # Check if environment already exists
        if data.name in manager:
            raise HTTPException(status_code=409, detail=f"Environment '{data.name}' already exists")

        # Create environment
        environ = Environ(
            name=data.name,
            description=data.description,
            options=data.options or {},
            mappings={}
        )

        # Add to manager
        manager.add(data.name, environ)

        # Save
        manager.save()

        return Result(data=environ)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/environments/{env_name}')
def update_environment(env_name: str, data: UpdateEnvironmentRequest, request: Request):
    """Update an existing environment"""
    try:
        manager = get_environ_manager(request)

        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        environ = manager[env_name]

        # Update environment attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'name' and value != env_name:
                # Handle name change - need to update manager key
                manager.remove(env_name)
                environ.name = value
                manager.add(value, environ)
            else:
                # Update other attributes
                if hasattr(environ, key):
                    setattr(environ, key, value)

        # Save
        manager.save()

        return Result(data=environ)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/environments/{env_name}')
def delete_environment(env_name: str, request: Request):
    """Delete an environment"""
    try:
        manager = get_environ_manager(request)

        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        # Remove from manager
        manager.remove(env_name)

        # Save
        manager.save()

        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/schemas')
def get_environment_schemas(env_name: str, request: Request):
    """Get environment-specific schemas"""
    try:
        manager = get_environ_manager(request)

        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        environ = manager[env_name]

        # Get schemas for this environment
        # This might need adjustment based on how environment-specific schemas are implemented
        project = get_project(request)
        schemas = []

        # If environment has specific schema configurations
        if hasattr(environ, 'schemas') and environ.schemas:
            schemas = list(environ.schemas.keys())
        else:
            # Fall back to project schemas
            schemas = list(project.schemas.keys()) if hasattr(project, 'schemas') else []

        return Result(data=schemas)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/databases')
def get_environment_databases(env_name: str, request: Request):
    """Get deployable databases for environment"""
    try:
        manager = get_environ_manager(request)

        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        environ = manager[env_name]

        # Get databases/mappings configured for this environment
        databases = []
        if hasattr(environ, 'mappings') and environ.mappings:
            for mapping_name, mapping in environ.mappings.items():
                if hasattr(mapping, 'deployment') and mapping.deployment:
                    databases.append({
                        'mapping_name': mapping_name,
                        'group': getattr(mapping, 'group', None),
                        'instances': getattr(mapping, 'instances', []),
                        'description': getattr(mapping, 'description', None)
                    })

        return Result(data=databases)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
