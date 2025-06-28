"""
Validation utilities for DBGear Web API

Provides validation helpers for API requests and schema validation.
"""
from typing import Any, Dict, List
from dbgear.models.schema import SchemaManager
from dbgear.models.table import Table
from dbgear.models.column import Column
from dbgear.models.column_type import parse_column_type, is_numeric_type, is_string_type


def validate_schema_name(schema_name: str) -> bool:
    """Validate schema name format"""
    if not schema_name or not isinstance(schema_name, str):
        return False
    return schema_name.replace('_', '').replace('-', '').isalnum()


def validate_table_name(table_name: str) -> bool:
    """Validate table name format"""
    if not table_name or not isinstance(table_name, str):
        return False
    return table_name.replace('_', '').replace('-', '').isalnum()


def validate_column_name(column_name: str) -> bool:
    """Validate column name format"""
    if not column_name or not isinstance(column_name, str):
        return False
    return column_name.replace('_', '').replace('-', '').isalnum()


def validate_column_type(column_type_str: str) -> Dict[str, Any]:
    """
    Validate column type string and return validation result
    
    Returns:
        dict: {
            'valid': bool,
            'column_type': ColumnType | None,
            'error': str | None
        }
    """
    try:
        column_type = parse_column_type(column_type_str)
        return {
            'valid': True,
            'column_type': column_type,
            'error': None
        }
    except Exception as e:
        return {
            'valid': False,
            'column_type': None,
            'error': str(e)
        }


def validate_foreign_key_reference(
    schemas: Dict[str, Any], 
    target_schema: str, 
    target_table: str, 
    target_column: str
) -> Dict[str, Any]:
    """
    Validate foreign key reference exists
    
    Returns:
        dict: {
            'valid': bool,
            'error': str | None
        }
    """
    if target_schema not in schemas:
        return {
            'valid': False,
            'error': f"Target schema '{target_schema}' not found"
        }
    
    schema = schemas[target_schema]
    if target_table not in schema.tables:
        return {
            'valid': False,
            'error': f"Target table '{target_table}' not found in schema '{target_schema}'"
        }
    
    table = schema.tables[target_table]
    if target_column not in table.columns:
        return {
            'valid': False,
            'error': f"Target column '{target_column}' not found in table '{target_schema}.{target_table}'"
        }
    
    return {
        'valid': True,
        'error': None
    }


def validate_primary_key_constraints(table: Table) -> Dict[str, Any]:
    """
    Validate primary key constraints for a table
    
    Returns:
        dict: {
            'valid': bool,
            'errors': List[str]
        }
    """
    errors = []
    pk_columns = [col for col in table.columns if col.primary_key is not None]
    
    # Check for duplicate primary key orders
    pk_orders = [col.primary_key for col in pk_columns if col.primary_key is not None]
    if len(pk_orders) != len(set(pk_orders)):
        errors.append("Duplicate primary key order numbers found")
    
    # Check for gaps in primary key sequence
    if pk_orders:
        pk_orders.sort()
        expected = list(range(1, len(pk_orders) + 1))
        if pk_orders != expected:
            errors.append("Primary key order numbers should be sequential starting from 1")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_table_constraints(table: Table, schemas: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validate all table constraints
    
    Returns:
        dict: {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str]
        }
    """
    errors = []
    warnings = []
    
    # Validate primary key constraints
    pk_result = validate_primary_key_constraints(table)
    if not pk_result['valid']:
        errors.extend(pk_result['errors'])
    
    # Validate column types
    for column in table.columns:
        if hasattr(column, 'column_type') and column.column_type:
            type_result = validate_column_type(str(column.column_type))
            if not type_result['valid']:
                errors.append(f"Invalid column type for '{column.column_name}': {type_result['error']}")
    
    # Validate foreign key references if schemas provided
    if schemas and hasattr(table, 'relations'):
        for relation in table.relations:
            fk_result = validate_foreign_key_reference(
                schemas, 
                relation.target_schema, 
                relation.target_table,
                relation.bind_columns[0].target if relation.bind_columns else ''
            )
            if not fk_result['valid']:
                errors.append(f"Foreign key validation failed: {fk_result['error']}")
    
    # Check for empty table
    if len(table.columns) == 0:
        warnings.append("Table has no columns defined")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }