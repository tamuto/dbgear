from fastapi import APIRouter, Request, HTTPException
from dbgear.models.column_type import ColumnType, ColumnTypeRegistry
from ..shared.dtos import Result, CreateColumnTypeRequest, UpdateColumnTypeRequest
from ..shared.helpers import get_schema_manager, save_schema_manager


router = APIRouter()


def get_column_type_registry(request: Request, schema_name: str) -> ColumnTypeRegistry:
    """Get or create column type registry for a schema"""
    manager = get_schema_manager(request)
    schema = manager[schema_name]
    
    if not hasattr(schema, 'column_type_registry'):
        schema.column_type_registry = ColumnTypeRegistry()
    
    return schema.column_type_registry


@router.get('/schemas/{schema_name}/column-types')
def get_column_types(schema_name: str, request: Request):
    """Get all column types for a schema"""
    try:
        registry = get_column_type_registry(request, schema_name)
        return Result(data=list(registry))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/column-types/{type_name}')
def get_column_type(schema_name: str, type_name: str, request: Request):
    """Get a specific column type"""
    try:
        registry = get_column_type_registry(request, schema_name)
        
        if type_name not in registry:
            raise HTTPException(status_code=404, detail="Column type not found")
        
        column_type = registry[type_name]
        return Result(data=column_type)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/column-types')
def create_column_type(schema_name: str, data: CreateColumnTypeRequest, request: Request):
    """Create a new column type"""
    try:
        registry = get_column_type_registry(request, schema_name)
        
        # Check if column type already exists
        if data.type_name in registry:
            raise HTTPException(status_code=409, detail=f"Column type '{data.type_name}' already exists")
        
        # Create column type
        column_type = ColumnType(
            column_type=data.type_name,
            base_type=data.base_type,
            length=data.length,
            precision=data.precision,
            scale=data.scale,
            items=data.items,
            description=data.description
        )
        
        # Add to registry
        registry.add(data.type_name, column_type)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=column_type)
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
        registry = get_column_type_registry(request, schema_name)
        
        if type_name not in registry:
            raise HTTPException(status_code=404, detail="Column type not found")
        
        column_type = registry[type_name]
        
        # Update column type attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'type_name':
                # Handle type name change - need to update registry key
                if value != type_name:
                    # Remove old key and add new one
                    registry.remove(type_name)
                    registry.add(value, column_type)
                    column_type.column_type = value
            else:
                # Update other attributes
                if hasattr(column_type, key):
                    setattr(column_type, key, value)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=column_type)
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
        registry = get_column_type_registry(request, schema_name)
        
        if type_name not in registry:
            raise HTTPException(status_code=404, detail="Column type not found")
        
        # Remove from registry
        registry.remove(type_name)
        
        # Save schema
        save_schema_manager(request)
        
        return Result()
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/column-types/{type_name}/validate')
def validate_column_type(schema_name: str, type_name: str, request: Request):
    """Validate a column type definition"""
    try:
        registry = get_column_type_registry(request, schema_name)
        
        if type_name not in registry:
            raise HTTPException(status_code=404, detail="Column type not found")
        
        column_type = registry[type_name]
        
        # Perform validation
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Basic validation checks
        if not column_type.base_type:
            validation_result['valid'] = False
            validation_result['errors'].append("base_type is required")
        
        # Check for conflicting attributes
        if column_type.base_type not in ['VARCHAR', 'CHAR'] and column_type.length is not None:
            validation_result['warnings'].append("length is not applicable for this base type")
        
        if column_type.base_type not in ['DECIMAL', 'NUMERIC'] and (column_type.precision is not None or column_type.scale is not None):
            validation_result['warnings'].append("precision/scale are not applicable for this base type")
        
        if column_type.base_type not in ['ENUM', 'SET'] and column_type.items is not None:
            validation_result['warnings'].append("items are not applicable for this base type")
        
        return Result(data=validation_result)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))