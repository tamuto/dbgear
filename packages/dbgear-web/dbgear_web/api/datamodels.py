from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException

from dbgear.models.datamodel import DataModel
from dbgear.models.datamodel import DataSource

from ..shared.dtos import Result
from ..shared.dtos import CreateDataModelRequest
from ..shared.dtos import UpdateDataModelRequest
from ..shared.dtos import ModifyDataSourceRequest
from ..shared.helpers import get_project

router = APIRouter()


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels')
def get_datamodels(env_name: str, mapping_name: str, request: Request):
    """Get all data models in a mapping"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        map = project.envs[env_name].mappings[mapping_name]
        return Result(data=list(map.datamodels))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}')
def get_datamodel(env_name: str, mapping_name: str, schema_name: str, table_name: str, request: Request):
    """Get a specific data model"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        map = project.envs[env_name].mappings[mapping_name]
        return Result(data=map.datamodel(schema_name, table_name))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments/{env_name}/mappings/{mapping_name}/datamodels')
def create_datamodel(env_name: str, mapping_name: str, data: CreateDataModelRequest, request: Request):
    """Create a new data model"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        map = project.envs[env_name].mappings[mapping_name]
        datamodel = DataModel(
            folder=map.folder,
            environ=map.environ,
            map_name=map.name,
            **data.model_dump(exclude_unset=True)
        )
        datamodel.save()
        return Result(data=datamodel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}')
def update_datamodel(env_name: str, mapping_name: str, schema_name: str, table_name: str, data: UpdateDataModelRequest, request: Request):
    """Update an existing data model"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        map = project.envs[env_name].mappings[mapping_name]
        datamodel = DataModel(
            folder=map.folder,
            environ=map.environ,
            map_name=map.name,
            schema_name=schema_name,
            table_name=table_name,
            **data.model_dump(exclude_unset=True)
        )
        datamodel.save()
        return Result(data=datamodel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}')
def delete_datamodel(env_name: str, mapping_name: str, schema_name: str, table_name: str, request: Request):
    """Delete a data model"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        map = project.envs[env_name].mappings[mapping_name]
        datamodel = map.datamodel(schema_name, table_name)
        datamodel.remove()
        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}/datasources')
def get_datasources(env_name: str, mapping_name: str, schema_name: str, table_name: str, request: Request):
    """Get data sources for a data model"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        map = project.envs[env_name].mappings[mapping_name]
        datamodel = map.datamodel(schema_name, table_name)
        return Result(data=list(datamodel.datasources))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}/datasources')
def modify_datasource(env_name: str, mapping_name: str, schema_name: str, table_name: str, data: ModifyDataSourceRequest, request: Request):
    """Create a new data source"""
    try:
        project = get_project(request)
        if env_name not in project.envs:
            raise HTTPException(status_code=404, detail="Environment not found")
        if mapping_name not in project.envs[env_name].mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")
        map = project.envs[env_name].mappings[mapping_name]
        datamodel = map.datamodel(schema_name, table_name)

        datasource = DataSource(
            folder=datamodel.folder,
            environ=datamodel.environ,
            name=datamodel.map_name,
            schema_name=datamodel.schema_name,
            table_name=datamodel.table_name,
            segment=data.segment
        )
        if len(data.data) == 0:
            datasource.remove()
            return Result()
        datasource.data = data.data
        datasource.save()
        return Result(data=datasource)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
