"""
Utility functions for data import operations.
"""

from typing import Any, Dict, List, Optional, Set


class JSONFieldProcessor:
    """
    Utility class for processing JSON fields with dot notation.
    """

    @staticmethod
    def process_json_fields(data: List[Dict[str, Any]], json_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Process JSON fields with dot notation into nested dictionaries.

        This function handles:
        - Dot notation expansion (e.g., 'user.profile.name' -> nested dict)
        - Merging multiple dot-notation fields into single JSON objects
        - Preserving existing nested structures

        Args:
            data: List of data rows
            json_fields: List of JSON field prefixes (e.g., ['user', 'settings'])

        Returns:
            Processed data with nested JSON structures
        """
        if not json_fields or not data:
            return data

        processed_data = []

        for row in data:
            processed_row = {}
            json_structures = {field: {} for field in json_fields}

            # Separate regular fields from JSON fields
            for field_name, value in row.items():
                json_field_found = False

                # Check if this field belongs to any JSON structure
                for json_field in json_fields:
                    if field_name.startswith(f"{json_field}."):
                        # This is a JSON field with dot notation
                        json_path = field_name[len(json_field) + 1:]  # Remove prefix and dot
                        JSONFieldProcessor._set_nested_value(json_structures[json_field], json_path, value)
                        json_field_found = True
                        break
                    elif field_name == json_field:
                        # This is the root JSON field
                        if isinstance(value, dict):
                            json_structures[json_field] = value
                        else:
                            json_structures[json_field] = value
                        json_field_found = True
                        break

                if not json_field_found:
                    # Regular field
                    processed_row[field_name] = value

            # Add JSON structures to the processed row
            for json_field, structure in json_structures.items():
                if structure:  # Only add if there's actual data
                    processed_row[json_field] = structure

            processed_data.append(processed_row)

        return processed_data

    @staticmethod
    def _set_nested_value(obj: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a nested value in a dictionary using dot notation.

        Args:
            obj: Target dictionary
            path: Dot-separated path (e.g., 'profile.name')
            value: Value to set
        """
        if not path:
            return

        parts = path.split('.')
        current = obj

        # Navigate to the parent of the final key
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Convert to dict if it's not already
                current[part] = {}
            current = current[part]

        # Set the final value
        current[parts[-1]] = value

    @staticmethod
    def detect_json_fields(data: List[Dict[str, Any]]) -> List[str]:
        """
        Automatically detect potential JSON fields based on dot notation in field names.

        Args:
            data: List of data rows

        Returns:
            List of detected JSON field prefixes
        """
        if not data:
            return []

        json_field_prefixes = set()

        for row in data:
            for field_name in row.keys():
                if '.' in field_name:
                    # Extract the prefix (everything before the first dot)
                    prefix = field_name.split('.')[0]
                    json_field_prefixes.add(prefix)

        return sorted(list(json_field_prefixes))

    @staticmethod
    def validate_json_structure(data: List[Dict[str, Any]], json_fields: List[str]) -> Dict[str, List[str]]:
        """
        Validate JSON field structures and return validation results.

        Args:
            data: List of data rows
            json_fields: List of JSON field prefixes to validate

        Returns:
            Dictionary with validation results:
            - 'valid': List of valid JSON fields
            - 'invalid': List of invalid JSON fields
            - 'warnings': List of warning messages
        """
        results = {
            'valid': [],
            'invalid': [],
            'warnings': []
        }

        if not data or not json_fields:
            return results

        for json_field in json_fields:
            field_paths = set()

            # Collect all paths for this JSON field
            for row in data:
                for field_name in row.keys():
                    if field_name.startswith(f"{json_field}."):
                        field_paths.add(field_name)
                    elif field_name == json_field:
                        field_paths.add(field_name)

            if field_paths:
                results['valid'].append(json_field)

                # Check for potential conflicts
                root_field_exists = json_field in field_paths
                nested_fields_exist = any(path.startswith(f"{json_field}.") for path in field_paths)

                if root_field_exists and nested_fields_exist:
                    results['warnings'].append(
                        f"JSON field '{json_field}' has both root value and nested fields"
                    )
            else:
                results['invalid'].append(json_field)

        return results


class DataValidator:
    """
    Utility class for validating imported data.
    """

    @staticmethod
    def validate_required_columns(data: List[Dict[str, Any]], required_columns: List[str]) -> Dict[str, Any]:
        """
        Validate that required columns are present in the data.

        Args:
            data: List of data rows
            required_columns: List of required column names

        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'missing_columns': [],
            'rows_with_missing_data': []
        }

        if not data:
            results['valid'] = False
            results['missing_columns'] = required_columns
            return results

        # Check if required columns exist in the data
        first_row_columns = set(data[0].keys())
        missing_columns = [col for col in required_columns if col not in first_row_columns]

        if missing_columns:
            results['valid'] = False
            results['missing_columns'] = missing_columns

        # Check for missing data in required columns
        for row_idx, row in enumerate(data):
            missing_in_row = []
            for col in required_columns:
                if col in row and (row[col] is None or row[col] == ''):
                    missing_in_row.append(col)

            if missing_in_row:
                results['rows_with_missing_data'].append({
                    'row_index': row_idx,
                    'missing_columns': missing_in_row
                })

        return results

    @staticmethod
    def validate_data_types(data: List[Dict[str, Any]], column_types: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate data types for specified columns.

        Args:
            data: List of data rows
            column_types: Dictionary mapping column names to expected types

        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'type_errors': []
        }

        for row_idx, row in enumerate(data):
            for col_name, expected_type in column_types.items():
                if col_name in row and row[col_name] is not None:
                    value = row[col_name]

                    # Simple type validation
                    if expected_type.lower() in ('int', 'integer') and not isinstance(value, int):
                        try:
                            int(value)
                        except (ValueError, TypeError):
                            results['type_errors'].append({
                                'row_index': row_idx,
                                'column': col_name,
                                'value': value,
                                'expected_type': expected_type
                            })
                    elif expected_type.lower() in ('float', 'decimal') and not isinstance(value, (int, float)):
                        try:
                            float(value)
                        except (ValueError, TypeError):
                            results['type_errors'].append({
                                'row_index': row_idx,
                                'column': col_name,
                                'value': value,
                                'expected_type': expected_type
                            })
                    elif expected_type.lower() in ('str', 'string', 'text') and not isinstance(value, str):
                        # String type validation is usually flexible
                        pass

        if results['type_errors']:
            results['valid'] = False

        return results
