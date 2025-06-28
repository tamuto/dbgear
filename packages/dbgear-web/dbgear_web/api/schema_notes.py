from fastapi import APIRouter, Request, HTTPException
from dbgear.models.notes import Note
from ..shared.dtos import Result, CreateNoteRequest, UpdateNoteRequest
from ..shared.helpers import get_schema_manager, save_schema_manager


router = APIRouter()


# Schema-level notes

@router.get('/schemas/{schema_name}/notes')
def get_schema_notes(schema_name: str, request: Request):
    """Get all notes for a schema"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        if hasattr(schema, 'notes'):
            return Result(data=list(schema.notes))
        else:
            return Result(data=[])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/notes')
def create_schema_note(schema_name: str, data: CreateNoteRequest, request: Request):
    """Create a new schema note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        # Create note
        note = Note(
            title=data.title,
            content=data.content,
            checked=data.checked
        )
        
        # Add to schema notes
        if not hasattr(schema, 'notes'):
            schema.notes = []
        schema.notes.append(note)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=note)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/notes/{note_index}')
def update_schema_note(schema_name: str, note_index: int, data: UpdateNoteRequest, request: Request):
    """Update a schema note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        if not hasattr(schema, 'notes') or note_index >= len(schema.notes):
            raise HTTPException(status_code=404, detail="Note not found")
        
        note = schema.notes[note_index]
        
        # Update note attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(note, key):
                setattr(note, key, value)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=note)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/notes/{note_index}')
def delete_schema_note(schema_name: str, note_index: int, request: Request):
    """Delete a schema note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        
        if not hasattr(schema, 'notes') or note_index >= len(schema.notes):
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Remove note
        del schema.notes[note_index]
        
        # Save schema
        save_schema_manager(request)
        
        return Result()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Table-level notes

@router.get('/schemas/{schema_name}/tables/{table_name}/notes')
def get_table_notes(schema_name: str, table_name: str, request: Request):
    """Get all notes for a table"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if hasattr(table, 'notes'):
            return Result(data=list(table.notes))
        else:
            return Result(data=[])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/tables/{table_name}/notes')
def create_table_note(schema_name: str, table_name: str, data: CreateNoteRequest, request: Request):
    """Create a new table note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        # Create note
        note = Note(
            title=data.title,
            content=data.content,
            checked=data.checked
        )
        
        # Add to table notes
        if not hasattr(table, 'notes'):
            table.notes = []
        table.notes.append(note)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=note)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/tables/{table_name}/notes/{note_index}')
def update_table_note(schema_name: str, table_name: str, note_index: int, data: UpdateNoteRequest, request: Request):
    """Update a table note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if not hasattr(table, 'notes') or note_index >= len(table.notes):
            raise HTTPException(status_code=404, detail="Note not found")
        
        note = table.notes[note_index]
        
        # Update note attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(note, key):
                setattr(note, key, value)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=note)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/tables/{table_name}/notes/{note_index}')
def delete_table_note(schema_name: str, table_name: str, note_index: int, request: Request):
    """Delete a table note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        
        if not hasattr(table, 'notes') or note_index >= len(table.notes):
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Remove note
        del table.notes[note_index]
        
        # Save schema
        save_schema_manager(request)
        
        return Result()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Column-level notes

@router.get('/schemas/{schema_name}/tables/{table_name}/columns/{column_name}/notes')
def get_column_notes(schema_name: str, table_name: str, column_name: str, request: Request):
    """Get all notes for a column"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        column = table.columns[column_name]
        
        if hasattr(column, 'notes'):
            return Result(data=list(column.notes))
        else:
            return Result(data=[])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/tables/{table_name}/columns/{column_name}/notes')
def create_column_note(schema_name: str, table_name: str, column_name: str, data: CreateNoteRequest, request: Request):
    """Create a new column note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        column = table.columns[column_name]
        
        # Create note
        note = Note(
            title=data.title,
            content=data.content,
            checked=data.checked
        )
        
        # Add to column notes
        if not hasattr(column, 'notes'):
            column.notes = []
        column.notes.append(note)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=note)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/tables/{table_name}/columns/{column_name}/notes/{note_index}')
def update_column_note(schema_name: str, table_name: str, column_name: str, note_index: int, data: UpdateNoteRequest, request: Request):
    """Update a column note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        column = table.columns[column_name]
        
        if not hasattr(column, 'notes') or note_index >= len(column.notes):
            raise HTTPException(status_code=404, detail="Note not found")
        
        note = column.notes[note_index]
        
        # Update note attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(note, key):
                setattr(note, key, value)
        
        # Save schema
        save_schema_manager(request)
        
        return Result(data=note)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/tables/{table_name}/columns/{column_name}/notes/{note_index}')
def delete_column_note(schema_name: str, table_name: str, column_name: str, note_index: int, request: Request):
    """Delete a column note"""
    try:
        manager = get_schema_manager(request)
        schema = manager[schema_name]
        table = schema.tables[table_name]
        column = table.columns[column_name]
        
        if not hasattr(column, 'notes') or note_index >= len(column.notes):
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Remove note
        del column.notes[note_index]
        
        # Save schema
        save_schema_manager(request)
        
        return Result()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))