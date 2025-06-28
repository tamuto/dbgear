from fastapi import APIRouter, Request, HTTPException
from dbgear.models.relation import Relation, EntityInfo, BindColumn
from ..shared.dtos import Result, CreateRelationRequest, UpdateRelationRequest
from ..shared.helpers import get_schema_manager, save_schema_manager


router = APIRouter()


@router.get('/schemas/{schema_name}/tables/{table_name}/relations')
def get_relations(schema_name: str, table_name: str, request: Request):
    """Get all relations for a table"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if hasattr(table, 'relations'):
            return Result(data=list(table.relations))
        else:
            return Result(data=[])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/tables/{table_name}/relations/{relation_index}')
def get_relation(schema_name: str, table_name: str, relation_index: int, request: Request):
    """Get a specific relation by index"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if not hasattr(table, 'relations') or relation_index >= len(table.relations):
            raise HTTPException(status_code=404, detail="Relation not found")
        
        relation = table.relations[relation_index]
        return Result(data=relation)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/tables/{table_name}/relations')
def create_relation(schema_name: str, table_name: str, data: CreateRelationRequest, request: Request):
    """Create a new relation"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        # Create EntityInfo for target
        target_entity = EntityInfo(
            schema_name=data.target_schema,
            table_name=data.target_table
        )
        
        # Create BindColumn objects
        bind_columns = []
        for bind in data.bind_columns:
            bind_column = BindColumn(
                source=bind["source"],
                target=bind["target"]
            )
            bind_columns.append(bind_column)
        
        # Create Relation
        relation = Relation(
            relation_name=data.relation_name,
            target=target_entity,
            bind_columns=bind_columns,
            on_delete=data.on_delete,
            on_update=data.on_update,
            logical_only=data.logical_only
        )
        
        # Add to table relations
        if not hasattr(table, 'relations'):
            table.relations = []
        table.relations.append(relation)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=relation)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/tables/{table_name}/relations/{relation_index}')
def update_relation(schema_name: str, table_name: str, relation_index: int, data: UpdateRelationRequest, request: Request):
    """Update an existing relation"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if not hasattr(table, 'relations') or relation_index >= len(table.relations):
            raise HTTPException(status_code=404, detail="Relation not found")
        
        relation = table.relations[relation_index]
        
        # Update relation attributes
        update_data = data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            if key == 'target_schema' or key == 'target_table':
                # Update target entity
                if key == 'target_schema':
                    relation.target.schema_name = value
                elif key == 'target_table':
                    relation.target.table_name = value
            elif key == 'bind_columns' and value is not None:
                # Update bind columns
                bind_columns = []
                for bind in value:
                    bind_column = BindColumn(
                        source=bind["source"],
                        target=bind["target"]
                    )
                    bind_columns.append(bind_column)
                relation.bind_columns = bind_columns
            else:
                # Update other attributes
                if hasattr(relation, key):
                    setattr(relation, key, value)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=relation)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/tables/{table_name}/relations/{relation_index}')
def delete_relation(schema_name: str, table_name: str, relation_index: int, request: Request):
    """Delete a relation"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if not hasattr(table, 'relations') or relation_index >= len(table.relations):
            raise HTTPException(status_code=404, detail="Relation not found")
        
        # Remove relation
        del table.relations[relation_index]
        
        # Save schema
        save_schema_manager(request)
        
        return Result()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))