from fastapi import APIRouter, Request, HTTPException
from dbgear.models.schema import SchemaManager
from dbgear.models.column import Column
from dbgear.models.column_type import parse_column_type
from ..shared.dtos import Result, CreateColumnRequest, UpdateColumnRequest, convert_to_column


router = APIRouter()


def get_schema_manager(request: Request) -> SchemaManager:
    """Get SchemaManager from request state"""
    if not hasattr(request.app.state, 'schema_manager'):
        request.app.state.schema_manager = SchemaManager()
        request.app.state.schema_manager.load('schema.yaml')
    return request.app.state.schema_manager


@router.get('/schemas/{schema_name}/tables/{table_name}/columns')
def get_columns(schema_name: str, table_name: str, request: Request):
    """Get all columns for a table"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        return Result(data=list(table.columns))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/tables/{table_name}/columns/{column_name}')
def get_column(schema_name: str, table_name: str, column_name: str, request: Request):
    """Get a specific column"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        column = table.columns[column_name]
        return Result(data=column)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/tables/{table_name}/columns')
def create_column(schema_name: str, table_name: str, data: CreateColumnRequest, request: Request):
    """Create a new column"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        # Check if column already exists
        if data.column_name in table.columns:
            raise HTTPException(status_code=409, detail=f"Column '{data.column_name}' already exists")
        
        # Parse column type
        column_type = parse_column_type(data.column_type)
        
        # Create column with parsed type
        column_data = data.model_dump(exclude_unset=True)
        column_data['column_type'] = column_type
        column = Column(**column_data)
        
        # Add to table
        table.columns.add(column)
        
        # Save schema
        manager.save('schema.yaml')
        
        return Result(data=column)
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/tables/{table_name}/columns/{column_name}')
def update_column(schema_name: str, table_name: str, column_name: str, data: UpdateColumnRequest, request: Request):
    """Update an existing column"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if column_name not in table.columns:
            raise HTTPException(status_code=404, detail=f"Column '{column_name}' not found")
        
        column = table.columns[column_name]
        
        # Update column attributes
        update_data = data.model_dump(exclude_unset=True)
        
        # Parse column type if provided
        if 'column_type' in update_data:
            update_data['column_type'] = parse_column_type(update_data['column_type'])
        
        # Update column
        for key, value in update_data.items():
            setattr(column, key, value)
        
        # Save schema
        manager.save('schema.yaml')
        
        return Result(data=column)
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/tables/{table_name}/columns/{column_name}')
def delete_column(schema_name: str, table_name: str, column_name: str, request: Request):
    """Delete a column"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if column_name not in table.columns:
            raise HTTPException(status_code=404, detail=f"Column '{column_name}' not found")
        
        # Remove column
        table.columns.remove(column_name)
        
        # Save schema
        manager.save('schema.yaml')
        
        return Result()
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))