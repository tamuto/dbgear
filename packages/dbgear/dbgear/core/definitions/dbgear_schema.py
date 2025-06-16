from typing import Any, Dict, Optional

from ..models.schema import Schema, Table, Field, Index, View, ViewColumn
from ..models.fileio import load_yaml


def parse_field_definition(field_data: Dict[str, Any]) -> Field:
    """Parse field definition from YAML data."""
    return Field(
        column_name=field_data['column_name'],
        display_name=field_data.get('display_name', field_data['column_name']),
        column_type=field_data['column_type'],
        nullable=field_data.get('nullable', True),
        primary_key=field_data.get('primary_key'),
        default_value=field_data.get('default_value'),
        foreign_key=field_data.get('foreign_key'),
        comment=field_data.get('comment'),
        expression=field_data.get('expression'),
        stored=field_data.get('stored', False),
        auto_increment=field_data.get('auto_increment', False),
        charset=field_data.get('charset'),
        collation=field_data.get('collation')
    )


def parse_index_definition(index_data: Dict[str, Any]) -> Index:
    """Parse index definition from YAML data."""
    return Index(
        index_name=index_data.get('index_name'),
        columns=index_data['columns']
    )


def parse_table_definition(table_name: str, table_data: Dict[str, Any], instance: str) -> Table:
    """Parse table definition from YAML data."""
    fields = []
    if 'fields' in table_data:
        for field_data in table_data['fields']:
            fields.append(parse_field_definition(field_data))

    indexes = []
    if 'indexes' in table_data:
        for index_data in table_data['indexes']:
            indexes.append(parse_index_definition(index_data))

    return Table(
        instance=instance,
        table_name=table_name,
        display_name=table_data.get('display_name', table_name),
        fields=fields,
        indexes=indexes
    )


def parse_view_definition(view_name: str, view_data: Dict[str, Any], instance: str) -> View:
    """Parse view definition from YAML data."""
    return View(
        instance=instance,
        view_name=view_name,
        display_name=view_data.get('display_name', view_name),
        select_statement=view_data['select_statement'],
        comment=view_data.get('comment')
    )


def retrieve(folder: str, filename: str, mapping: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Schema]:
    """Retrieve schema definitions from YAML file."""
    file_path = f'{folder}/{filename}'

    schema_data = load_yaml(file_path)

    if 'schemas' not in schema_data:
        raise ValueError(f"Schema file {filename} must contain 'schemas' key")

    schemas = {}

    for schema_name, schema_content in schema_data['schemas'].items():
        # Apply mapping if provided
        instance_name = mapping.get(schema_name, schema_name) if mapping else schema_name

        schema = Schema(instance_name)

        if 'tables' in schema_content:
            for table_name, table_data in schema_content['tables'].items():
                table = parse_table_definition(table_name, table_data, instance_name)
                schema.add_table(table)

        if 'views' in schema_content:
            for view_name, view_data in schema_content['views'].items():
                view = parse_view_definition(view_name, view_data, instance_name)
                schema.add_view(view)

        schemas[instance_name] = schema

    return schemas
