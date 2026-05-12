"""
Command definitions for dbgear-doc plugin.

This module provides CLI subcommand registration and execution
for the dbgear documentation plugin.
"""

import logging
from pathlib import Path

from .generator import generate_docs
from .er_diagram import generate_svg, generate_drawio


def register_commands(subparsers):
    """
    Register all subcommands provided by this plugin.

    Args:
        subparsers: argparse subparsers object from the main CLI.

    Returns:
        List of registered command names.
    """
    _register_doc_command(subparsers)
    _register_svg_command(subparsers)
    _register_drawio_command(subparsers)

    return ['doc', 'svg', 'drawio']


def execute(args, project):
    """
    Execute the specified subcommand.

    Args:
        args: Parsed command line arguments.
        project: The loaded project object.

    Returns:
        True if execution was successful, False otherwise.
    """
    schema_path = Path(project.folder) / 'schema.yaml'

    if not schema_path.exists():
        logging.error(f'schema.yaml not found: {schema_path}')
        return False

    if args.command == 'doc':
        return _execute_doc(args, schema_path)
    elif args.command == 'svg':
        return _execute_svg(args, schema_path)
    elif args.command == 'drawio':
        return _execute_drawio(args, schema_path)

    return False


def _register_doc_command(subparsers):
    """Register the doc subcommand."""
    parser = subparsers.add_parser('doc', help='generate documentation from schema')
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='output path: file path for schema scope, directory for table scope'
    )
    parser.add_argument(
        '--template',
        required=True,
        help='Jinja2 template file path'
    )
    parser.add_argument(
        '--scope',
        choices=['schema', 'table', 'view', 'trigger', 'procedure'],
        default='table',
        help='data scope: schema (1 file), table/view/trigger/procedure (per-entity files)'
    )


def _register_svg_command(subparsers):
    """Register the svg subcommand."""
    parser = subparsers.add_parser('svg', help='generate ER diagram in SVG format')
    parser.add_argument(
        '-o', '--output',
        default='./er_diagram.svg',
        help='output file path (default: ./er_diagram.svg)'
    )
    parser.add_argument(
        '-s', '--schema',
        help='schema name (uses first schema if not specified)'
    )
    parser.add_argument(
        '-t', '--table',
        nargs='+',
        help='center table name(s); accepts "schema.table" for cross-schema diagrams '
             '(shows all tables in the default schema if not specified)'
    )
    parser.add_argument(
        '--table-file',
        help='path to a file listing center table names (one per line, # for comments; '
             'each entry may be qualified as "schema.table")'
    )
    parser.add_argument(
        '--referenced-by-level',
        type=int,
        default=1,
        help='levels of tables that reference this table to include '
             '(default: 1; ignored when multiple center tables are specified)'
    )
    parser.add_argument(
        '--references-level',
        type=int,
        default=1,
        help='levels of tables this table references to include '
             '(default: 1; ignored when multiple center tables are specified)'
    )


def _register_drawio_command(subparsers):
    """Register the drawio subcommand."""
    parser = subparsers.add_parser('drawio', help='generate ER diagram in draw.io format')
    parser.add_argument(
        '-o', '--output',
        default='./er_diagram.drawio',
        help='output file path (default: ./er_diagram.drawio)'
    )
    parser.add_argument(
        '-s', '--schema',
        help='schema name (uses first schema if not specified)'
    )
    parser.add_argument(
        '-t', '--table',
        nargs='+',
        help='center table name(s); accepts "schema.table" for cross-schema diagrams '
             '(shows all tables in the default schema if not specified)'
    )
    parser.add_argument(
        '--table-file',
        help='path to a file listing center table names (one per line, # for comments; '
             'each entry may be qualified as "schema.table")'
    )
    parser.add_argument(
        '--referenced-by-level',
        type=int,
        default=1,
        help='levels of tables that reference this table to include '
             '(default: 1; ignored when multiple center tables are specified)'
    )
    parser.add_argument(
        '--references-level',
        type=int,
        default=1,
        help='levels of tables this table references to include '
             '(default: 1; ignored when multiple center tables are specified)'
    )


def _execute_doc(args, schema_path):
    """Execute the doc command."""
    generated_files = generate_docs(
        schema_path=str(schema_path),
        output_dir=args.output,
        template=args.template,
        scope=args.scope,
    )
    logging.info(f'Generated {len(generated_files)} documentation files in {args.output}')
    return True


def _execute_svg(args, schema_path):
    """Execute the svg command."""
    center_tables = _resolve_center_tables(args)
    generate_svg(
        schema_path=str(schema_path),
        output_path=args.output,
        schema_name=args.schema,
        center_tables=center_tables,
        referenced_by_level=args.referenced_by_level,
        references_level=args.references_level,
    )
    logging.info(f'Generated ER diagram: {args.output}')
    return True


def _execute_drawio(args, schema_path):
    """Execute the drawio command."""
    center_tables = _resolve_center_tables(args)
    generate_drawio(
        schema_path=str(schema_path),
        output_path=args.output,
        schema_name=args.schema,
        center_tables=center_tables,
        referenced_by_level=args.referenced_by_level,
        references_level=args.references_level,
    )
    logging.info(f'Generated ER diagram: {args.output}')
    return True


def _resolve_center_tables(args) -> list[str] | None:
    """
    Combine ``--table`` and ``--table-file`` into a deduplicated, order-preserving list.

    Returns None when neither option supplies any name (treated as "all tables").
    Raises ValueError when ``--table-file`` is given but yields no entries.
    """
    names: list[str] = []
    seen: set[str] = set()

    def _add(name: str) -> None:
        if name and name not in seen:
            seen.add(name)
            names.append(name)

    if args.table:
        for name in args.table:
            _add(name)

    if args.table_file:
        file_names = _read_table_file(args.table_file)
        if not file_names:
            raise ValueError(f'table file is empty: {args.table_file}')
        for name in file_names:
            _add(name)

    return names or None


def _read_table_file(path: str) -> list[str]:
    """Read table names from a file, skipping blank lines and ``#`` comments."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f'table file not found: {path}')

    names: list[str] = []
    with open(file_path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.split('#', 1)[0].strip()
            if line:
                names.append(line)
    return names
