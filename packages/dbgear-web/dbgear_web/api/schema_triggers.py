from fastapi import APIRouter, Request, HTTPException
from dbgear.models.trigger import Trigger
from ..shared.dtos import Result, CreateTriggerRequest, UpdateTriggerRequest
from ..shared.helpers import get_schema_manager, save_schema_manager


router = APIRouter()


@router.get('/schemas/{schema_name}/triggers')
def get_triggers(schema_name: str, request: Request):
    """Get all triggers for a schema"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        if hasattr(schema, 'triggers'):
            return Result(data=list(schema.triggers))
        else:
            return Result(data=[])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/triggers/{trigger_name}')
def get_trigger(schema_name: str, trigger_name: str, request: Request):
    """Get a specific trigger"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        if not hasattr(schema, 'triggers'):
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        trigger = None
        for t in schema.triggers:
            if t.trigger_name == trigger_name:
                trigger = t
                break
        
        if trigger is None:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        return Result(data=trigger)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/triggers')
def create_trigger(schema_name: str, data: CreateTriggerRequest, request: Request):
    """Create a new trigger"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        # Check if trigger already exists
        if hasattr(schema, 'triggers'):
            for t in schema.triggers:
                if t.trigger_name == data.trigger_name:
                    raise HTTPException(status_code=409, detail=f"Trigger '{data.trigger_name}' already exists")
        
        # Create trigger
        trigger = Trigger(
            trigger_name=data.trigger_name,
            table_name=data.table_name,
            timing=data.timing,
            event=data.event,
            statement=data.statement,
            comment=data.comment
        )
        
        # Add to schema triggers
        if not hasattr(schema, 'triggers'):
            schema.triggers = []
        schema.triggers.append(trigger)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=trigger)
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/triggers/{trigger_name}')
def update_trigger(schema_name: str, trigger_name: str, data: UpdateTriggerRequest, request: Request):
    """Update an existing trigger"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        if not hasattr(schema, 'triggers'):
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        trigger = None
        for t in schema.triggers:
            if t.trigger_name == trigger_name:
                trigger = t
                break
        
        if trigger is None:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        # Update trigger attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(trigger, key):
                setattr(trigger, key, value)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=trigger)
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/triggers/{trigger_name}')
def delete_trigger(schema_name: str, trigger_name: str, request: Request):
    """Delete a trigger"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        if not hasattr(schema, 'triggers'):
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        # Find and remove trigger
        trigger_index = None
        for i, t in enumerate(schema.triggers):
            if t.trigger_name == trigger_name:
                trigger_index = i
                break
        
        if trigger_index is None:
            raise HTTPException(status_code=404, detail="Trigger not found")
        
        # Remove trigger
        del schema.triggers[trigger_index]
        
        # Save schema
        save_schema_manager(request)
        
        return Result()
    except HTTPException:
        raise
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))