"""
Base data importer class providing common functionality.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

from dbgear.models.schema import SchemaManager
from .utils import JSONFieldProcessor, DataValidator


class BaseDataImporter(ABC):
    """
    Base class for data importers providing common functionality.
    """

    def __init__(self, schema: SchemaManager, table_name: str, schema_name: str = 'main'):
        """
        Initialize the data importer.

        Args:
            schema: Schema manager containing table definitions
            table_name: Name of the target table
            schema_name: Name of the schema (default: 'main')
        """
        self.schema = schema
        self.table_name = table_name
        self.schema_name = schema_name
        self.table = None

        # Get table definition
        if schema_name in schema.schemas:
            schema_obj = schema.schemas[schema_name]
            if table_name in schema_obj.tables:
                self.table = schema_obj.tables[table_name]
            else:
                raise ValueError(f"Table '{table_name}' not found in schema '{schema_name}'")
        else:
            raise ValueError(f"Schema '{schema_name}' not found")

    @abstractmethod
    def read_data(self, source: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Read data from source file.

        Args:
            source: Path to source file
            **kwargs: Additional arguments

        Returns:
            List of dictionaries representing rows
        """
        pass

    def process_json_fields(self, data: List[Dict[str, Any]], json_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Process JSON fields with dot notation into nested dictionaries.

        Args:
            data: List of data rows
            json_fields: List of field names that should be treated as JSON paths

        Returns:
            Processed data with nested JSON structures
        """
        return JSONFieldProcessor.process_json_fields(data, json_fields)

    def validate_columns(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate column names and types against schema.

        Args:
            data: List of data rows

        Returns:
            Validated data
        """
        if not data:
            return data

        # Get column names from table definition
        table_columns = {col.column_name for col in self.table.columns}

        validated_data = []
        for row in data:
            validated_row = {}
            for col_name, value in row.items():
                if col_name in table_columns:
                    validated_row[col_name] = value
                else:
                    # Log warning for unknown columns
                    print(f"Warning: Column '{col_name}' not found in table '{self.table_name}' schema")

            validated_data.append(validated_row)

        return validated_data

    def write_dat_file(self, data: List[Dict[str, Any]], output_path: str) -> str:
        """
        Write data to .dat file in YAML format.

        Args:
            data: List of data rows
            output_path: Directory path for output file

        Returns:
            Path to the created .dat file
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename: {schema}@{table}.dat
        filename = f"{self.schema_name}@{self.table_name}.dat"
        file_path = output_dir / filename

        # Write YAML data
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return str(file_path)

    def import_data(self, source: str, output_path: str, json_fields: Optional[List[str]] = None, **kwargs) -> str:
        """
        Import data from source and write to .dat file.

        Args:
            source: Path to source file
            output_path: Directory path for output file
            json_fields: List of field names that should be treated as JSON paths
            **kwargs: Additional arguments

        Returns:
            Path to the created .dat file
        """
        # Read data from source
        data = self.read_data(source, **kwargs)

        # Process JSON fields if specified
        if json_fields:
            data = self.process_json_fields(data, json_fields)

        # Validate columns against schema
        data = self.validate_columns(data)

        # Write to .dat file
        return self.write_dat_file(data, output_path)
