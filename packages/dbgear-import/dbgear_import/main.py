"""
Main CLI entry point for dbgear-import.
"""

import argparse
import sys
from pathlib import Path

from .importer import import_schema, list_importers


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

    # Data import command (placeholder for future)
    data_parser = subparsers.add_parser('data', help='Import initial data (future)')
    data_parser.add_argument('format', help='Data format (excel, csv)')
    data_parser.add_argument('source_file', help='Source file to import')
    data_parser.add_argument('--schema', help='Schema YAML file', required=True)
    data_parser.add_argument('--table', help='Target table name', required=True)

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
    """Handle data import command (placeholder)."""
    print("Data import functionality is not yet implemented.", file=sys.stderr)
    print("This feature will be available in a future release.", file=sys.stderr)
    return 1


def handle_list_importers(args):
    """Handle list importers command."""
    importers = list_importers()
    if importers:
        print("Available schema importers:")
        for importer in importers:
            print(f"  - {importer}")
    else:
        print("No importers available.")
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