from fastapi import APIRouter, Request, HTTPException
from dbgear.models.environ import EnvironManager
from dbgear.models.datamodel import DataModel, DataSource, DataModelManager
from ..shared.dtos import Result, CreateDataModelRequest, UpdateDataModelRequest, CreateDataSourceRequest, UpdateDataSourceRequest
from ..shared.helpers import get_project
import os
import yaml


router = APIRouter()


def get_environ_manager(request: Request) -> EnvironManager:
    """Get EnvironManager from project"""
    project = get_project(request)
    return EnvironManager(project.folder)


def get_datamodel_manager(project_folder: str, env_name: str, mapping_name: str) -> DataModelManager:
    """Get DataModelManager for a specific mapping"""
    mapping_path = f"{project_folder}/{env_name}/{mapping_name}"
    return DataModelManager(mapping_path)


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels')
def get_datamodels(env_name: str, mapping_name: str, request: Request):
    """Get all data models in a mapping"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        manager = get_datamodel_manager(project.folder, env_name, mapping_name)
        
        return Result(data=list(manager))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}')
def get_datamodel(env_name: str, mapping_name: str, schema_name: str, table_name: str, request: Request):
    """Get a specific data model"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        manager = get_datamodel_manager(project.folder, env_name, mapping_name)
        
        datamodel_key = f"{schema_name}@{table_name}"
        if datamodel_key not in manager:
            raise HTTPException(status_code=404, detail="Data model not found")
        
        datamodel = manager[datamodel_key]
        return Result(data=datamodel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments/{env_name}/mappings/{mapping_name}/datamodels')
def create_datamodel(env_name: str, mapping_name: str, data: CreateDataModelRequest, request: Request):
    """Create a new data model"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        manager = get_datamodel_manager(project.folder, env_name, mapping_name)
        
        # Create data model
        datamodel = DataModel(
            id=f"{data.description}",  # This might need to be derived differently
            instance="",  # This would typically be set based on the context
            table_name="",  # This would typically be set based on the context
            description=data.description,
            layout=data.layout,
            settings=data.settings or {},
            sync_mode=data.sync_mode,
            value=data.value,
            caption=data.caption,
            segment=data.segment,
            x_axis=data.x_axis,
            y_axis=data.y_axis,
            cells=data.cells
        )
        
        # Add to manager
        manager.add(datamodel.id, datamodel)
        
        # Save
        manager.save()
        
        return Result(data=datamodel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}')
def update_datamodel(env_name: str, mapping_name: str, schema_name: str, table_name: str, data: UpdateDataModelRequest, request: Request):
    """Update an existing data model"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        manager = get_datamodel_manager(project.folder, env_name, mapping_name)
        
        datamodel_key = f"{schema_name}@{table_name}"
        if datamodel_key not in manager:
            raise HTTPException(status_code=404, detail="Data model not found")
        
        datamodel = manager[datamodel_key]
        
        # Update data model attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(datamodel, key):
                setattr(datamodel, key, value)
        
        # Save
        manager.save()
        
        return Result(data=datamodel)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}')
def delete_datamodel(env_name: str, mapping_name: str, schema_name: str, table_name: str, request: Request):
    """Delete a data model"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        manager = get_datamodel_manager(project.folder, env_name, mapping_name)
        
        datamodel_key = f"{schema_name}@{table_name}"
        if datamodel_key not in manager:
            raise HTTPException(status_code=404, detail="Data model not found")
        
        # Remove data model
        manager.remove(datamodel_key)
        
        # Save
        manager.save()
        
        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}/datasources')
def get_datasources(env_name: str, mapping_name: str, schema_name: str, table_name: str, request: Request):
    """Get data sources for a data model"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        
        # Look for data files
        data_path = f"{project.folder}/{env_name}/{mapping_name}"
        datasources = []
        
        try:
            import glob
            
            # Look for .dat files matching the schema@table pattern
            pattern = f"{data_path}/{schema_name}@{table_name}*.dat"
            dat_files = glob.glob(pattern)
            
            for dat_file in dat_files:
                filename = os.path.basename(dat_file)
                # Parse segment from filename if present
                base_name = filename.replace('.dat', '')
                parts = base_name.split('#')
                segment = parts[1] if len(parts) > 1 else None
                
                # Try to read the data file
                try:
                    with open(dat_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        datasource = DataSource(
                            segment=segment,
                            data=data if isinstance(data, list) else []
                        )
                        datasources.append(datasource)
                except Exception:
                    # If we can't read the file, create a placeholder
                    datasources.append(DataSource(
                        segment=segment,
                        data=[]
                    ))
        except Exception:
            # If we can't access the directory, return empty list
            pass
        
        return Result(data=datasources)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}/datasources/{segment}')
def get_datasource(env_name: str, mapping_name: str, schema_name: str, table_name: str, segment: str, request: Request):
    """Get a specific data source"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        
        # Construct filename
        filename = f"{schema_name}@{table_name}"
        if segment != "default":
            filename += f"#{segment}"
        filename += ".dat"
        
        data_file = f"{project.folder}/{env_name}/{mapping_name}/{filename}"
        
        if not os.path.exists(data_file):
            raise HTTPException(status_code=404, detail="Data source not found")
        
        # Read the data file
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                datasource = DataSource(
                    segment=segment if segment != "default" else None,
                    data=data if isinstance(data, list) else []
                )
                return Result(data=datasource)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading data file: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}/datasources')
def create_datasource(env_name: str, mapping_name: str, schema_name: str, table_name: str, data: CreateDataSourceRequest, request: Request):
    """Create a new data source"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        
        # Construct filename
        filename = f"{schema_name}@{table_name}"
        if data.segment:
            filename += f"#{data.segment}"
        filename += ".dat"
        
        data_file = f"{project.folder}/{env_name}/{mapping_name}/{filename}"
        
        # Check if file already exists
        if os.path.exists(data_file):
            raise HTTPException(status_code=409, detail="Data source already exists")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        # Write the data file
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                yaml.dump(data.data, f, default_flow_style=False, allow_unicode=True)
            
            datasource = DataSource(
                segment=data.segment,
                data=data.data
            )
            return Result(data=datasource)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing data file: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}/datasources/{segment}')
def update_datasource(env_name: str, mapping_name: str, schema_name: str, table_name: str, segment: str, data: UpdateDataSourceRequest, request: Request):
    """Update an existing data source"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        
        # Construct filename
        filename = f"{schema_name}@{table_name}"
        if segment != "default":
            filename += f"#{segment}"
        filename += ".dat"
        
        data_file = f"{project.folder}/{env_name}/{mapping_name}/{filename}"
        
        if not os.path.exists(data_file):
            raise HTTPException(status_code=404, detail="Data source not found")
        
        # Write the data file
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                yaml.dump(data.data, f, default_flow_style=False, allow_unicode=True)
            
            datasource = DataSource(
                segment=segment if segment != "default" else None,
                data=data.data
            )
            return Result(data=datasource)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing data file: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/environments/{env_name}/mappings/{mapping_name}/datamodels/{schema_name}@{table_name}/datasources/{segment}')
def delete_datasource(env_name: str, mapping_name: str, schema_name: str, table_name: str, segment: str, request: Request):
    """Delete a data source"""
    try:
        environ_manager = get_environ_manager(request)
        
        if env_name not in environ_manager:
            raise HTTPException(status_code=404, detail="Environment not found")
        
        project = get_project(request)
        
        # Construct filename
        filename = f"{schema_name}@{table_name}"
        if segment != "default":
            filename += f"#{segment}"
        filename += ".dat"
        
        data_file = f"{project.folder}/{env_name}/{mapping_name}/{filename}"
        
        if not os.path.exists(data_file):
            raise HTTPException(status_code=404, detail="Data source not found")
        
        # Delete the file
        try:
            os.remove(data_file)
            return Result()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting data file: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))