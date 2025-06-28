from fastapi import APIRouter, Request, HTTPException
from dbgear.models.environ import EnvironManager
from dbgear.models.mapping import Mapping
from ..shared.dtos import Result, CreateMappingRequest, UpdateMappingRequest
from ..shared.helpers import get_project


router = APIRouter()


def get_environ_manager(request: Request) -> EnvironManager:
    """Get EnvironManager from project"""
    project = get_project(request)
    return EnvironManager(project.folder)


@router.get('/environments/{env_name}/mappings')
def get_mappings(env_name: str, request: Request):
    """Get all mappings in an environment"""
    try:
        manager = get_environ_manager(request)
        
        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        environ = manager[env_name]
        
        if hasattr(environ, 'mappings'):
            return Result(data=list(environ.mappings.values()))
        else:
            return Result(data=[])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}')
def get_mapping(env_name: str, mapping_name: str, request: Request):
    """Get a specific mapping"""
    try:
        manager = get_environ_manager(request)
        
        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        environ = manager[env_name]
        
        if not hasattr(environ, 'mappings') or mapping_name not in environ.mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        mapping = environ.mappings[mapping_name]
        return Result(data=mapping)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments/{env_name}/mappings')
def create_mapping(env_name: str, data: CreateMappingRequest, request: Request):
    """Create a new mapping in an environment"""
    try:
        manager = get_environ_manager(request)
        
        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        environ = manager[env_name]
        
        # Check if mapping already exists
        if hasattr(environ, 'mappings') and data.name in environ.mappings:
            raise HTTPException(status_code=409, detail=f"Mapping '{data.name}' already exists")
        
        # Create mapping
        mapping = Mapping(
            id=data.name,
            name=data.name,
            group=data.group,
            base=data.base,
            instances=data.instances or [],
            description=data.description,
            deployment=data.deployment
        )
        
        # Add to environment mappings
        if not hasattr(environ, 'mappings'):
            environ.mappings = {}
        environ.mappings[data.name] = mapping
        
        # Save
        manager.save()
        
        return Result(data=mapping)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/environments/{env_name}/mappings/{mapping_name}')
def update_mapping(env_name: str, mapping_name: str, data: UpdateMappingRequest, request: Request):
    """Update an existing mapping"""
    try:
        manager = get_environ_manager(request)
        
        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        environ = manager[env_name]
        
        if not hasattr(environ, 'mappings') or mapping_name not in environ.mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        mapping = environ.mappings[mapping_name]
        
        # Update mapping attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'name' and value != mapping_name:
                # Handle name change - need to update mapping key
                del environ.mappings[mapping_name]
                mapping.name = value
                mapping.id = value
                environ.mappings[value] = mapping
            else:
                # Update other attributes
                if hasattr(mapping, key):
                    setattr(mapping, key, value)
        
        # Save
        manager.save()
        
        return Result(data=mapping)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/environments/{env_name}/mappings/{mapping_name}')
def delete_mapping(env_name: str, mapping_name: str, request: Request):
    """Delete a mapping"""
    try:
        manager = get_environ_manager(request)
        
        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        environ = manager[env_name]
        
        if not hasattr(environ, 'mappings') or mapping_name not in environ.mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        # Remove mapping
        del environ.mappings[mapping_name]
        
        # Save
        manager.save()
        
        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels')
def get_mapping_datamodels(env_name: str, mapping_name: str, request: Request):
    """Get data models associated with a mapping"""
    try:
        manager = get_environ_manager(request)
        
        if env_name not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        environ = manager[env_name]
        
        if not hasattr(environ, 'mappings') or mapping_name not in environ.mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        
        # Get data models for this mapping
        # This would typically involve looking at the data model files in the mapping directory
        project = get_project(request)
        datamodel_path = f"{project.folder}/{env_name}/{mapping_name}"
        
        # List available data models (this is a simplified implementation)
        datamodels = []
        try:
            import os
            import glob
            
            if os.path.exists(datamodel_path):
                yaml_files = glob.glob(f"{datamodel_path}/*.yaml")
                for yaml_file in yaml_files:
                    filename = os.path.basename(yaml_file)
                    if filename != 'datamodel.yaml':  # Skip the main datamodel file
                        # Parse schema@table format
                        base_name = filename.replace('.yaml', '')
                        if '@' in base_name:
                            schema_name, table_name = base_name.split('@', 1)
                            datamodels.append({
                                'schema_name': schema_name,
                                'table_name': table_name,
                                'file_name': filename
                            })
        except Exception:
            # If we can't read the directory, return empty list
            pass
        
        return Result(data=datamodels)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))