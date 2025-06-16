from typing import Dict, List, Optional
from pathlib import Path
import os

from .schema import Schema, Table, Field, Index
from .fileio import load_yaml, save_yaml
from ..definitions.dbgear_schema import retrieve


class SchemaValidator:
    """Schema validation utilities."""

    @staticmethod
    def validate_table(table: Table) -> List[str]:
        """Validate table structure and return list of error messages."""
        errors = []

        if not table.table_name:
            errors.append("Table name is required")

        if not table.fields:
            errors.append("Table must have at least one field")

        # Check for duplicate field names
        field_names = [field.column_name for field in table.fields]
        if len(field_names) != len(set(field_names)):
            errors.append("Duplicate field names found")

        # Validate each field
        for field in table.fields:
            field_errors = SchemaValidator.validate_field(field)
            errors.extend([f"Field '{field.column_name}': {error}" for error in field_errors])

        return errors

    @staticmethod
    def validate_field(field: Field) -> List[str]:
        """Validate field definition and return list of error messages."""
        errors = []

        if not field.column_name:
            errors.append("Column name is required")

        if not field.column_type:
            errors.append("Column type is required")

        # Validate primary key value
        if field.primary_key is not None and field.primary_key < 1:
            errors.append("Primary key order must be positive integer")

        return errors

    @staticmethod
    def validate_foreign_key(field: Field, schemas: Dict[str, Schema]) -> List[str]:
        """Validate foreign key reference and return list of error messages."""
        errors = []

        if not field.foreign_key:
            return errors

        # Parse foreign key reference (e.g., "table_name.column_name")
        if '.' not in field.foreign_key:
            errors.append("Foreign key must be in format 'table_name.column_name'")
            return errors

        table_name, column_name = field.foreign_key.split('.', 1)

        # Find referenced table in any schema
        referenced_table = None
        for schema in schemas.values():
            if schema.table_exists(table_name):
                referenced_table = schema.get_table(table_name)
                break

        if not referenced_table:
            errors.append(f"Referenced table '{table_name}' not found")
            return errors

        if not referenced_table.field_exists(column_name):
            errors.append(f"Referenced column '{column_name}' not found in table '{table_name}'")

        return errors


class SchemaManager:
    """Manages schema CRUD operations and persistence."""

    def __init__(self, project_folder: str, schema_file: str = "schema.yaml"):
        self.project_folder = Path(project_folder)
        self.schema_file = schema_file
        self.schema_path = self.project_folder / schema_file
        self._schemas: Dict[str, Schema] = {}

        # Load existing schemas if file exists
        if self.schema_path.exists():
            self.reload()

    def reload(self) -> None:
        """Reload schemas from file."""
        if self.schema_path.exists():
            self._schemas = retrieve(str(self.project_folder), self.schema_file)

    def save(self) -> None:
        """Save current schemas to file."""
        schema_data = {"schemas": {}}

        for schema_name, schema in self._schemas.items():
            schema_data["schemas"][schema_name] = {
                "tables": {}
            }

            for table_name, table in schema.get_tables().items():
                table_dict = {
                    "display_name": table.display_name,
                    "fields": []
                }

                for field in table.fields:
                    field_dict = {
                        "column_name": field.column_name,
                        "display_name": field.display_name,
                        "column_type": field.column_type,
                        "nullable": field.nullable
                    }

                    if field.primary_key is not None:
                        field_dict["primary_key"] = field.primary_key
                    if field.default_value is not None:
                        field_dict["default_value"] = field.default_value
                    if field.foreign_key is not None:
                        field_dict["foreign_key"] = field.foreign_key
                    if field.comment is not None:
                        field_dict["comment"] = field.comment

                    table_dict["fields"].append(field_dict)

                if table.indexes:
                    table_dict["indexes"] = []
                    for index in table.indexes:
                        index_dict = {
                            "columns": index.columns
                        }
                        if index.index_name:
                            index_dict["index_name"] = index.index_name
                        table_dict["indexes"].append(index_dict)

                schema_data["schemas"][schema_name]["tables"][table_name] = table_dict

        save_yaml(str(self.schema_path), schema_data)

    def get_schemas(self) -> Dict[str, Schema]:
        """Get all schemas."""
        return self._schemas.copy()

    def get_schema(self, schema_name: str) -> Schema:
        """Get schema by name."""
        if schema_name not in self._schemas:
            raise KeyError(f"Schema '{schema_name}' not found")
        return self._schemas[schema_name]

    def schema_exists(self, schema_name: str) -> bool:
        """Check if schema exists."""
        return schema_name in self._schemas

    def create_schema(self, schema_name: str) -> Schema:
        """Create new schema."""
        if schema_name in self._schemas:
            raise ValueError(f"Schema '{schema_name}' already exists")

        schema = Schema(schema_name)
        self._schemas[schema_name] = schema
        return schema

    def delete_schema(self, schema_name: str) -> None:
        """Delete schema."""
        if schema_name not in self._schemas:
            raise KeyError(f"Schema '{schema_name}' not found")
        del self._schemas[schema_name]

    # Table operations
    def add_table(self, schema_name: str, table: Table) -> None:
        """Add table to schema."""
        schema = self.get_schema(schema_name)

        # Validate table
        errors = SchemaValidator.validate_table(table)
        if errors:
            raise ValueError(f"Table validation failed: {'; '.join(errors)}")

        # Validate foreign key references
        for field in table.fields:
            fk_errors = SchemaValidator.validate_foreign_key(field, self._schemas)
            if fk_errors:
                raise ValueError(f"Foreign key validation failed for field '{field.column_name}': {'; '.join(fk_errors)}")

        schema.add_table(table)

    def update_table(self, schema_name: str, table_name: str, table: Table) -> None:
        """Update existing table."""
        schema = self.get_schema(schema_name)

        # Validate table
        errors = SchemaValidator.validate_table(table)
        if errors:
            raise ValueError(f"Table validation failed: {'; '.join(errors)}")

        # Validate foreign key references
        for field in table.fields:
            fk_errors = SchemaValidator.validate_foreign_key(field, self._schemas)
            if fk_errors:
                raise ValueError(f"Foreign key validation failed for field '{field.column_name}': {'; '.join(fk_errors)}")

        schema.update_table(table_name, table)

    def delete_table(self, schema_name: str, table_name: str) -> None:
        """Delete table from schema."""
        schema = self.get_schema(schema_name)

        # Check for references to this table
        for other_schema in self._schemas.values():
            for other_table in other_schema.get_tables().values():
                for field in other_table.fields:
                    if field.foreign_key and field.foreign_key.startswith(f"{table_name}."):
                        raise ValueError(f"Cannot delete table '{table_name}': referenced by field '{field.column_name}' in table '{other_table.table_name}'")

        schema.remove_table(table_name)

    def get_table(self, schema_name: str, table_name: str) -> Table:
        """Get table by name."""
        schema = self.get_schema(schema_name)
        return schema.get_table(table_name)

    # Field operations
    def add_field(self, schema_name: str, table_name: str, field: Field) -> None:
        """Add field to table."""
        table = self.get_table(schema_name, table_name)

        # Validate field
        errors = SchemaValidator.validate_field(field)
        if errors:
            raise ValueError(f"Field validation failed: {'; '.join(errors)}")

        # Validate foreign key reference
        fk_errors = SchemaValidator.validate_foreign_key(field, self._schemas)
        if fk_errors:
            raise ValueError(f"Foreign key validation failed: {'; '.join(fk_errors)}")

        table.add_field(field)

    def update_field(self, schema_name: str, table_name: str, field_name: str, field: Field) -> None:
        """Update existing field."""
        table = self.get_table(schema_name, table_name)

        # Validate field
        errors = SchemaValidator.validate_field(field)
        if errors:
            raise ValueError(f"Field validation failed: {'; '.join(errors)}")

        # Validate foreign key reference
        fk_errors = SchemaValidator.validate_foreign_key(field, self._schemas)
        if fk_errors:
            raise ValueError(f"Foreign key validation failed: {'; '.join(fk_errors)}")

        table.update_field(field_name, field)

    def delete_field(self, schema_name: str, table_name: str, field_name: str) -> None:
        """Delete field from table."""
        table = self.get_table(schema_name, table_name)

        # Check for foreign key references to this field
        for other_schema in self._schemas.values():
            for other_table in other_schema.get_tables().values():
                for other_field in other_table.fields:
                    if other_field.foreign_key == f"{table_name}.{field_name}":
                        raise ValueError(f"Cannot delete field '{field_name}': referenced by field '{other_field.column_name}' in table '{other_table.table_name}'")

        table.remove_field(field_name)

    # Index operations
    def add_index(self, schema_name: str, table_name: str, index: Index) -> None:
        """Add index to table."""
        table = self.get_table(schema_name, table_name)

        # Validate that all index columns exist in the table
        for column_name in index.columns:
            if not table.field_exists(column_name):
                raise ValueError(f"Index column '{column_name}' does not exist in table '{table_name}'")

        table.add_index(index)

    def delete_index(self, schema_name: str, table_name: str, index_name: str) -> None:
        """Delete index from table."""
        table = self.get_table(schema_name, table_name)
        table.remove_index(index_name)
