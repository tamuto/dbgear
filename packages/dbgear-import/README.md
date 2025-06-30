# DBGear Import

Schema and data import functionality for DBGear.

## Features

- **Schema Import**: Import database schemas from various formats
  - A5:SQL Mk-2 (.a5er) format support
- **Data Import**: Import initial data from various formats (future)
  - Excel (.xlsx) format support (planned)
  - CSV format support (planned)

## Installation

```bash
# Basic installation
pip install dbgear-import

# With Excel support
pip install dbgear-import[excel]

# With CSV support  
pip install dbgear-import[csv]

# With all import formats
pip install dbgear-import[all]
```

## Usage

### Schema Import

```bash
# Import A5:SQL Mk-2 schema
dbgear-import schema a5sql_mk2 schema.a5er --output schema.yaml

# With schema mapping
dbgear-import schema a5sql_mk2 schema.a5er --mapping "MAIN:production,TEST:development"
```

### Data Import (Future)

```bash
# Import Excel data
dbgear-import data excel data.xlsx --schema schema.yaml --table users

# Import CSV data
dbgear-import data csv data.csv --schema schema.yaml --table products
```

## Dependencies

- `dbgear`: Core DBGear package
- `openpyxl`: Excel file processing (optional)
- `pandas`: Data manipulation (optional)
- `chardet`: Character encoding detection (optional)