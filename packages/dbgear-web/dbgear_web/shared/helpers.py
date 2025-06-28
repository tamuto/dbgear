"""
Helper utilities for DBGear Web API

Provides general utility functions for common tasks.
"""
from fastapi import Request
from dbgear.models.schema import SchemaManager
from dbgear.models.project import Project
from typing import Optional, Dict, Any
import os


def get_schema_manager(request: Request, schema_file: str = 'schema.yaml') -> SchemaManager:
    """
    Get SchemaManager from request state with lazy loading
    
    Args:
        request: FastAPI request object
        schema_file: Schema file name to load
        
    Returns:
        SchemaManager: Loaded schema manager instance
    """
    state_key = f'schema_manager_{schema_file}'
    
    if not hasattr(request.app.state, state_key):
        manager = SchemaManager()
        if os.path.exists(schema_file):
            manager.load(schema_file)
        setattr(request.app.state, state_key, manager)
    
    return getattr(request.app.state, state_key)


def get_project(request: Request) -> Project:
    """
    Get Project from request state
    
    Args:
        request: FastAPI request object
        
    Returns:
        Project: Project instance
        
    Raises:
        RuntimeError: If project is not found in app state
    """
    if hasattr(request.app.state, 'project'):
        return request.app.state.project
    raise RuntimeError("Project not found in application state")


def save_schema_manager(request: Request, schema_file: str = 'schema.yaml') -> None:
    """
    Save schema manager to file
    
    Args:
        request: FastAPI request object
        schema_file: Schema file name to save to
    """
    manager = get_schema_manager(request, schema_file)
    manager.save(schema_file)


def clear_schema_cache(request: Request, schema_file: str = 'schema.yaml') -> None:
    """
    Clear schema manager cache to force reload
    
    Args:
        request: FastAPI request object
        schema_file: Schema file name to clear from cache
    """
    state_key = f'schema_manager_{schema_file}'
    if hasattr(request.app.state, state_key):
        delattr(request.app.state, state_key)


def get_request_user(request: Request) -> Optional[str]:
    """
    Get user information from request (placeholder for future auth)
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: User identifier if available
    """
    # Placeholder for future authentication implementation
    return request.headers.get('X-User-ID')


def get_request_tenant(request: Request) -> Optional[str]:
    """
    Get tenant information from request (placeholder for future multi-tenancy)
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Tenant identifier if available
    """
    # Placeholder for future multi-tenancy implementation
    return request.headers.get('X-Tenant-ID')


def format_error_message(error: Exception, context: str = None) -> str:
    """
    Format error message for API responses
    
    Args:
        error: Exception instance
        context: Additional context information
        
    Returns:
        str: Formatted error message
    """
    base_message = str(error)
    if context:
        return f"{context}: {base_message}"
    return base_message


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized


def get_env_var(key: str, default: Any = None, required: bool = False) -> Any:
    """
    Get environment variable with validation
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Any: Environment variable value
        
    Raises:
        ValueError: If required variable is not found
    """
    value = os.environ.get(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' not found")
    
    return value


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def extract_query_params(request: Request, allowed_params: list = None) -> Dict[str, Any]:
    """
    Extract and validate query parameters from request
    
    Args:
        request: FastAPI request object
        allowed_params: List of allowed parameter names
        
    Returns:
        Dict[str, Any]: Extracted parameters
    """
    params = {}
    
    for key, value in request.query_params.items():
        if allowed_params is None or key in allowed_params:
            # Try to convert to appropriate type
            if value.lower() in ['true', 'false']:
                params[key] = value.lower() == 'true'
            elif value.isdigit():
                params[key] = int(value)
            else:
                params[key] = value
    
    return params