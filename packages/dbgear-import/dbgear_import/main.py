"""
Main CLI entry point for dbgear-import.
"""

import argparse
import sys
from pathlib import Path

from .importer import import_schema, list_importers, import_data, list_data_importers
from dbgear.models.schema import SchemaManager


def create_parser():
    """Create the argument parser for dbgear-import."""
    parser = argparse.ArgumentParser(
        prog='dbgear-import',
        description='Import schemas and data into DBGear format'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Schema import command
    schema_parser = subparsers.add_parser('schema', help='Import database schemas')
    schema_parser.add_argument('importer_type', help='Type of importer (e.g., a5sql_mk2)')
    schema_parser.add_argument('source_file', help='Source file to import')
    schema_parser.add_argument('--output', '-o', help='Output YAML file', default='schema.yaml')
    schema_parser.add_argument('--mapping', '-m', help='Schema mapping (e.g., "MAIN:main,TEST:test")')

    # Data import command
    data_parser = subparsers.add_parser('data', help='Import initial data')
    data_parser.add_argument('format', help='Data format (excel, csv)')
    data_parser.add_argument('source_file', help='Source file to import')
    data_parser.add_argument('--schema', help='Schema YAML file', required=True)
    data_parser.add_argument('--table', help='Target table name', required=True)
    data_parser.add_argument('--output', '-o', help='Output directory', default='.')
    data_parser.add_argument('--schema-name', help='Schema name (default: main)', default='main')
    data_parser.add_argument('--json-fields', help='JSON field names (comma-separated)')
    
    # Excel-specific options
    data_parser.add_argument('--sheet', help='Excel sheet name')
    data_parser.add_argument('--header-row', type=int, help='Header row number (default: 1)', default=1)
    data_parser.add_argument('--start-row', type=int, help='First data row number')
    data_parser.add_argument('--start-col', type=int, help='First data column number', default=1)
    data_parser.add_argument('--end-col', type=int, help='Last data column number')
    
    # CSV-specific options
    data_parser.add_argument('--encoding', help='CSV file encoding (default: auto-detect)')
    data_parser.add_argument('--delimiter', help='CSV delimiter (default: auto-detect)')
    data_parser.add_argument('--skip-rows', type=int, help='Number of rows to skip', default=0)

    # List available importers
    list_parser = subparsers.add_parser('list', help='List available importers')

    return parser


def handle_schema_import(args):
    """Handle schema import command."""
    # Parse mapping if provided
    mapping = {}
    if args.mapping:
        for pair in args.mapping.split(','):
            if ':' in pair:
                key, value = pair.split(':', 1)
                mapping[key.strip().upper()] = value.strip()

    # Get source file path
    source_path = Path(args.source_file)
    if not source_path.exists():
        print(f"Error: Source file '{args.source_file}' not found", file=sys.stderr)
        return 1

    try:
        # Import schema
        schema_manager = import_schema(
            args.importer_type,
            str(source_path.parent),
            source_path.name,
            mapping
        )

        # Save to output file
        schema_manager.save(args.output)
        print(f"Schema imported successfully to '{args.output}'")
        
        # Print summary
        total_tables = sum(len(schema.tables.tables) for schema in schema_manager.schemas.values())
        print(f"Imported {len(schema_manager.schemas)} schema(s) with {total_tables} table(s)")
        
        return 0

    except Exception as e:
        print(f"Error importing schema: {e}", file=sys.stderr)
        return 1


def handle_data_import(args):
    """Handle data import command."""
    # Check if source file exists
    source_path = Path(args.source_file)
    if not source_path.exists():
        print(f"Error: Source file '{args.source_file}' not found", file=sys.stderr)
        return 1
    
    # Check if schema file exists
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file '{args.schema}' not found", file=sys.stderr)
        return 1
    
    try:
        # Load schema
        schema_manager = SchemaManager()
        schema_manager.load(args.schema)
        
        # Parse JSON fields if provided
        json_fields = None
        if args.json_fields:
            json_fields = [field.strip() for field in args.json_fields.split(',')]
        
        # Prepare kwargs for format-specific options
        kwargs = {}
        
        if args.format == 'excel':
            if args.sheet:
                kwargs['sheet_name'] = args.sheet
            kwargs['header_row'] = args.header_row
            if args.start_row:
                kwargs['start_row'] = args.start_row
            kwargs['start_col'] = args.start_col
            if args.end_col:
                kwargs['end_col'] = args.end_col
                
        elif args.format == 'csv':
            if args.encoding:
                kwargs['encoding'] = args.encoding
            if args.delimiter:
                kwargs['delimiter'] = args.delimiter
            kwargs['skip_rows'] = args.skip_rows
        
        # Import data
        output_file = import_data(
            args.format,
            str(source_path),
            schema_manager,
            args.table,
            args.output,
            args.schema_name,
            json_fields,
            **kwargs
        )
        
        print(f"Data imported successfully to '{output_file}'")
        
        # Print summary
        with open(output_file, 'r', encoding='utf-8') as f:
            import yaml
            data = yaml.safe_load(f)
            if data:
                print(f"Imported {len(data)} row(s) to table '{args.table}'")
            else:
                print("No data imported (empty result)")
        
        return 0
        
    except Exception as e:
        print(f"Error importing data: {e}", file=sys.stderr)
        return 1


def handle_list_importers(args):
    """Handle list importers command."""
    schema_importers = list_importers()
    data_importers = list_data_importers()
    
    if schema_importers:
        print("Available schema importers:")
        for importer in schema_importers:
            print(f"  - {importer}")
    else:
        print("No schema importers available.")
    
    print()
    
    if data_importers:
        print("Available data importers:")
        for importer in data_importers:
            print(f"  - {importer}")
    else:
        print("No data importers available.")
    
    return 0


def execute():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'schema':
        return handle_schema_import(args)
    elif args.command == 'data':
        return handle_data_import(args)
    elif args.command == 'list':
        return handle_list_importers(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(execute())