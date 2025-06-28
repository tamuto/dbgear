"""
Model conversion utilities for DBGear Web API

Provides utilities for converting between API DTOs and core models.
"""
from typing import Dict, Any, List
from dbgear.models.schema import Schema, SchemaManager
from dbgear.models.table import Table
from dbgear.models.column import Column
from dbgear.models.view import View
from dbgear.models.index import Index
from dbgear.models.relation import Relation
from dbgear.models.column_type import parse_column_type


def schema_to_dict(schema: Schema) -> Dict[str, Any]:
    """Convert Schema model to dictionary for API response"""
    return {
        'schema_name': schema.schema_name,
        'display_name': schema.display_name,
        'tables': {name: table_to_dict(table) for name, table in schema.tables.items()},
        'views': {name: view_to_dict(view) for name, view in schema.views.items()},
        'notes': [note_to_dict(note) for note in schema.notes] if hasattr(schema, 'notes') else []
    }


def table_to_dict(table: Table) -> Dict[str, Any]:
    """Convert Table model to dictionary for API response"""
    return {
        'instance': table.instance,
        'table_name': table.table_name,
        'display_name': table.display_name,
        'columns': [column_to_dict(col) for col in table.columns],
        'indexes': [index_to_dict(idx) for idx in table.indexes] if hasattr(table, 'indexes') else [],
        'relations': [relation_to_dict(rel) for rel in table.relations] if hasattr(table, 'relations') else [],
        'notes': [note_to_dict(note) for note in table.notes] if hasattr(table, 'notes') else [],
        'mysql_options': table.mysql_options.model_dump() if hasattr(table, 'mysql_options') and table.mysql_options else None
    }


def column_to_dict(column: Column) -> Dict[str, Any]:
    """Convert Column model to dictionary for API response"""
    return {
        'column_name': column.column_name,
        'display_name': column.display_name,
        'column_type': str(column.column_type) if hasattr(column, 'column_type') else None,
        'nullable': column.nullable,
        'primary_key': column.primary_key,
        'default_value': column.default_value,
        'expression': column.expression,
        'stored': column.stored,
        'auto_increment': column.auto_increment,
        'charset': column.charset,
        'collation': column.collation,
        'notes': [note_to_dict(note) for note in column.notes] if hasattr(column, 'notes') else []
    }


def view_to_dict(view: View) -> Dict[str, Any]:
    """Convert View model to dictionary for API response"""
    return {
        'instance': view.instance,
        'view_name': view.view_name,
        'display_name': view.display_name,
        'select_statement': view.select_statement,
        'notes': [note_to_dict(note) for note in view.notes] if hasattr(view, 'notes') else []
    }


def index_to_dict(index: Index) -> Dict[str, Any]:
    """Convert Index model to dictionary for API response"""
    return {
        'index_name': index.index_name,
        'columns': index.columns,
        'unique': index.unique,
        'index_type': index.index_type,
        'partial_condition': index.partial_condition,
        'include_columns': index.include_columns,
        'storage_parameters': index.storage_parameters
    }


def relation_to_dict(relation: Relation) -> Dict[str, Any]:
    """Convert Relation model to dictionary for API response"""
    return {
        'relation_name': relation.relation_name,
        'target_schema': relation.target.schema_name,
        'target_table': relation.target.table_name,
        'bind_columns': [
            {
                'source': bind.source,
                'target': bind.target
            }
            for bind in relation.bind_columns
        ],
        'on_delete': relation.on_delete,
        'on_update': relation.on_update,
        'logical_only': relation.logical_only
    }


def note_to_dict(note) -> Dict[str, Any]:
    """Convert Note model to dictionary for API response"""
    return {
        'title': note.title,
        'content': note.content,
        'checked': note.checked
    }


def dict_to_schema(data: Dict[str, Any]) -> Schema:
    """Convert dictionary to Schema model"""
    return Schema(
        schema_name=data['schema_name'],
        display_name=data.get('display_name', data['schema_name']),
        tables={},  # Tables will be added separately
        views={},   # Views will be added separately
    )


def dict_to_table(data: Dict[str, Any]) -> Table:
    """Convert dictionary to Table model"""
    table = Table(
        instance=data['instance'],
        table_name=data['table_name'],
        display_name=data.get('display_name', data['table_name']),
        columns=[],  # Columns will be added separately
        indexes=[]   # Indexes will be added separately
    )
    
    # Add MySQL options if present
    if 'mysql_options' in data and data['mysql_options']:
        from dbgear.models.table import MySQLTableOptions
        table.mysql_options = MySQLTableOptions(**data['mysql_options'])
    
    return table


def dict_to_column(data: Dict[str, Any]) -> Column:
    """Convert dictionary to Column model"""
    column_data = data.copy()
    
    # Parse column type if it's a string
    if 'column_type' in column_data and isinstance(column_data['column_type'], str):
        column_data['column_type'] = parse_column_type(column_data['column_type'])
    
    return Column(**column_data)


def dict_to_view(data: Dict[str, Any]) -> View:
    """Convert dictionary to View model"""
    return View(
        instance=data['instance'],
        view_name=data['view_name'],
        display_name=data.get('display_name', data['view_name']),
        select_statement=data['select_statement']
    )


def dict_to_index(data: Dict[str, Any]) -> Index:
    """Convert dictionary to Index model"""
    return Index(**data)


def paginate_results(items: List[Any], page: int = 1, per_page: int = 50) -> Dict[str, Any]:
    """Paginate a list of items"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': end < total,
            'has_prev': page > 1
        }
    }


def filter_items(items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter items based on provided filters"""
    if not filters:
        return items
    
    filtered_items = []
    for item in items:
        match = True
        for key, value in filters.items():
            if key not in item or item[key] != value:
                match = False
                break
        if match:
            filtered_items.append(item)
    
    return filtered_items