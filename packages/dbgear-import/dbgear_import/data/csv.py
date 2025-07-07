"""
CSV data importer using standard csv library.
"""

import csv
import chardet
from typing import Any, Dict, List, Optional
from pathlib import Path

from .base import BaseDataImporter


class CSVDataImporter(BaseDataImporter):
    """
    CSV data importer using standard csv library.
    """

    def read_data(self, source: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Read data from CSV file.

        Args:
            source: Path to CSV file
            **kwargs: Additional arguments
                - encoding: File encoding (default: auto-detect)
                - delimiter: Field delimiter (default: auto-detect)
                - quotechar: Quote character (default: '"')
                - skip_rows: Number of rows to skip at the beginning (default: 0)
                - header_row: Row number containing headers (default: 0 after skipping)
                - max_rows: Maximum number of data rows to read (default: None - read all)

        Returns:
            List of dictionaries representing rows
        """
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"CSV file not found: {source}")

        # Detect encoding
        encoding = kwargs.get('encoding')
        if not encoding:
            encoding = self._detect_encoding(source_path)

        # Read file and detect delimiter
        with open(source_path, 'r', encoding=encoding) as f:
            sample = f.read(1024)
            delimiter = kwargs.get('delimiter')
            if not delimiter:
                delimiter = self._detect_delimiter(sample)

        # Read CSV data
        data = []
        skip_rows = kwargs.get('skip_rows', 0)
        header_row = kwargs.get('header_row', 0)
        max_rows = kwargs.get('max_rows')
        quotechar = kwargs.get('quotechar', '"')

        with open(source_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)

            # Skip initial rows
            for _ in range(skip_rows):
                next(reader, None)

            # Read headers
            headers = None
            for row_idx, row in enumerate(reader):
                if row_idx == header_row:
                    headers = [col.strip() for col in row]
                    break

            if not headers:
                raise ValueError("No headers found in CSV file")

            # Read data rows
            data_rows_read = 0
            for row in reader:
                if max_rows and data_rows_read >= max_rows:
                    break

                # Skip empty rows
                if not any(cell.strip() for cell in row if cell is not None):
                    continue

                # Create row dictionary
                row_data = {}
                for col_idx, header in enumerate(headers):
                    if col_idx < len(row):
                        cell_value = row[col_idx].strip() if row[col_idx] else None
                        row_data[header] = self._convert_cell_value(cell_value)
                    else:
                        row_data[header] = None

                data.append(row_data)
                data_rows_read += 1

        return data

    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding using chardet.

        Args:
            file_path: Path to the file

        Returns:
            Detected encoding
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'

    def _detect_delimiter(self, sample: str) -> str:
        """
        Detect CSV delimiter from sample text.

        Args:
            sample: Sample text from CSV file

        Returns:
            Detected delimiter
        """
        try:
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            return delimiter
        except Exception:
            # Fallback to comma if detection fails
            return ','

    def _convert_cell_value(self, value: Optional[str]) -> Any:
        """
        Convert CSV cell value to appropriate Python type.

        Args:
            value: Cell value as string

        Returns:
            Converted value
        """
        if value is None or value == '':
            return None

        # Handle special values
        if value.upper() in ('NOW()', 'CURRENT_TIMESTAMP'):
            return 'NOW()'
        elif value.upper() in ('SYSTEM', 'CURRENT_USER'):
            return 'SYSTEM'
        elif value.upper() in ('NULL', 'NONE'):
            return None

        # Handle quoted strings (like '''SYSTEM''')
        if value.startswith("'''") and value.endswith("'''"):
            return value

        # Try to convert to boolean
        if value.upper() in ('TRUE', 'YES', '1'):
            return True
        elif value.upper() in ('FALSE', 'NO', '0'):
            return False

        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Return as string
        return value


def import_data(source: str, schema, table_name: str, output_path: str,
                schema_name: str = 'main', json_fields: Optional[List[str]] = None,
                **kwargs) -> str:
    """
    Import data from CSV file and write to .dat file.

    Args:
        source: Path to CSV file
        schema: Schema manager containing table definitions
        table_name: Name of the target table
        output_path: Directory path for output file
        schema_name: Name of the schema (default: 'main')
        json_fields: List of field names that should be treated as JSON paths
        **kwargs: Additional arguments for CSV reading

    Returns:
        Path to the created .dat file
    """
    importer = CSVDataImporter(schema, table_name, schema_name)
    return importer.import_data(source, output_path, json_fields, **kwargs)
