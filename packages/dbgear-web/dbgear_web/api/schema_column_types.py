from fastapi import APIRouter
from fastapi import Request
from fastapi import HTTPException

from ..shared.dtos import Result
from ..shared.dtos import CreateColumnTypeRequest
from ..shared.dtos import UpdateColumnTypeRequest
from ..shared.helpers import get_project

router = APIRouter()


@router.get('/schemas/{schema_name}/column-types')
def get_column_types(schema_name: str, request: Request):
    """Get all column types for a schema"""
    try:
        project = get_project(request)
        return Result(data=list(project.registry))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/column-types/{type_name}')
def get_column_type(schema_name: str, type_name: str, request: Request):
    """Get a specific column type"""
    try:
        column_type = {}
        return Result(data=column_type)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/column-types')
def create_column_type(schema_name: str, data: CreateColumnTypeRequest, request: Request):
    """Create a new column type"""
    try:
        return Result(data={})
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/column-types/{type_name}')
def update_column_type(schema_name: str, type_name: str, data: UpdateColumnTypeRequest, request: Request):
    """Update an existing column type"""
    try:
        return Result(data={})
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/column-types/{type_name}')
def delete_column_type(schema_name: str, type_name: str, request: Request):
    """Delete a column type"""
    try:
        return Result()
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
