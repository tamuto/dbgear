"""
Response utilities for DBGear Web API

Provides standardized response helpers and error handling utilities.
"""
from fastapi import HTTPException
from dbgear.models.exceptions import (
    DBGearError, 
    DBGearEntityExistsError, 
    DBGearEntityNotFoundError, 
    DBGearEntityRemovalError
)
from .dtos import Result


def handle_dbgear_exceptions(func):
    """Decorator to handle DBGear exceptions and convert to HTTP responses"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DBGearEntityExistsError as e:
            raise HTTPException(status_code=409, detail=f"Entity already exists: {e}")
        except DBGearEntityNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"Entity not found: {e}")
        except DBGearEntityRemovalError as e:
            raise HTTPException(status_code=400, detail=f"Cannot remove entity: {e}")
        except DBGearError as e:
            raise HTTPException(status_code=500, detail=f"DBGear error: {e}")
        except KeyError as e:
            raise HTTPException(status_code=404, detail=f"Not found: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper


def success_response(data=None, message=None):
    """Create a successful response"""
    return Result(status='OK', data=data, message=message)


def error_response(message: str, status: str = 'ERROR'):
    """Create an error response"""
    return Result(status=status, message=message)


def not_found_response(entity: str, identifier: str = None):
    """Create a not found response"""
    message = f"{entity} not found"
    if identifier:
        message += f": {identifier}"
    return Result(status='ERROR', message=message)


def already_exists_response(entity: str, identifier: str = None):
    """Create an already exists response"""
    message = f"{entity} already exists"
    if identifier:
        message += f": {identifier}"
    return Result(status='ERROR', message=message)