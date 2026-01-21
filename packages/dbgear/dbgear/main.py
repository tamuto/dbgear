import logging
from argparse import ArgumentParser
from importlib.metadata import entry_points


def execute():
    parser = ArgumentParser(
        prog='dbgear',
        description='database management tools'
    )
    parser.add_argument(
        '--project',
        default='database',
        help='please specify the folder for the project.')

    sub = parser.add_subparsers(dest='command', help='sub-command help')

    apply_parser = sub.add_parser('apply', help='apply help')
    apply_parser.add_argument(
        'deploy',
        help='target deployment.')
    apply_parser.add_argument(
        'env',
        help='target environment.')
    apply_parser.add_argument(
        '--database',
        help='target database.')
    apply_parser.add_argument(
        '--target',
        help='target table.')
    apply_parser.add_argument(
        '--all',
        choices=['drop', 'delta'],
        help='apply all tables. Specify "drop" to drop database before applying, or "delta" to apply only the changes since the last deployment.'
    )
    apply_parser.add_argument(
        '--no-restore',
        action='store_true',
        help='skip all data operations (initial data loading and backup restoration)'
    )
    apply_parser.add_argument(
        '--restore-only',
        action='store_true',
        help='restore initial data only without recreating schema'
    )
    apply_parser.add_argument(
        '--patch',
        help='patch file to execute instead of restore'
    )
    apply_parser.add_argument(
        '--backup-key',
        help='backup table timestamp key (YYYYMMDDHHMMSS). Only valid with --restore-only'
    )
    apply_parser.add_argument(
        '--index-only',
        action='store_true',
        help='recreate indexes only for the specified table (only valid with --target, not with --all)'
    )
    apply_parser.add_argument(
        '--restore-backup',
        action='store_true',
        help='restore data from backup even if datamodel is not defined (only valid with --target)'
    )
    apply_parser.add_argument(
        '--dryrun',
        action='store_true',
        help='print SQL statements without executing them'
    )

    # doc subcommand - documentation generation
    doc_parser = sub.add_parser('doc', help='generate documentation from schema')
    doc_parser.add_argument(
        '-o', '--output',
        default='./docs',
        help='output directory for documentation (default: ./docs)'
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    if args.command is None:
        parser.print_help()
        return

    # For other commands, load project and required modules
    from .models.project import Project
    from . import operations

    project = Project.load(args.project)

    if args.command == 'apply':
        if not args.all and args.target is None:
            logging.error('please specify --target or --all')
            return

        # Validate backup-key option
        if args.backup_key and not args.restore_only:
            logging.error('--backup-key can only be used with --restore-only')
            return

        # Validate backup-key format
        if args.backup_key:
            import re
            if not re.match(r'^\d{14}$', args.backup_key):
                logging.error('--backup-key must be in YYYYMMDDHHMMSS format')
                return

        # Validate index-only option
        if args.index_only:
            if args.all:
                logging.error('--index-only cannot be used with --all')
                return
            if not args.target:
                logging.error('--index-only requires --target to specify a table')
                return

        # Validate restore-backup option
        if args.restore_backup:
            if args.all:
                logging.error('--restore-backup cannot be used with --all')
                return
            if not args.target:
                logging.error('--restore-backup requires --target to specify a table')
                return

        operations.apply(
            project,
            args.env,
            args.database,
            args.target,
            args.all,
            args.deploy,
            args.no_restore,
            args.restore_only,
            args.patch,
            args.backup_key,
            args.index_only,
            args.restore_backup,
            args.dryrun
        )

    elif args.command == 'doc':
        # Load doc plugin via entry points
        eps = entry_points(group='dbgear.plugins')
        doc_ep = None
        for ep in eps:
            if ep.name == 'doc':
                doc_ep = ep
                break

        if doc_ep is None:
            logging.error('doc plugin not found. Please install dbgear-doc package.')
            return

        from pathlib import Path

        generate_docs = doc_ep.load()
        schema_path = Path(project.folder) / 'schema.yaml'

        if not schema_path.exists():
            logging.error(f'schema.yaml not found: {schema_path}')
            return

        generated_files = generate_docs(
            schema_path=str(schema_path),
            output_dir=args.output,
        )
        logging.info(f'Generated {len(generated_files)} documentation files in {args.output}')
