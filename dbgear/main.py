import logging
from argparse import ArgumentParser

from .models.project import Project
from . import backend
from . import operations


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
    sub.add_parser('serve', help='serve help')

    apply_parser = sub.add_parser('apply', help='apply help')
    apply_parser.add_argument(
        'deploy',
        help='target deployment.')
    apply_parser.add_argument(
        'env',
        help='target environment.')
    apply_parser.add_argument(
        '--target',
        help='target table.')
    apply_parser.add_argument(
        '--all',
        action='store_true',
        help='apply all tables.')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    if args.command is None:
        parser.print_help()
        return

    project = Project(args.project)
    project.read_definitions()

    if args.command == 'serve':
        backend.run(project)
    if args.command == 'apply':
        if not args.all and args.target is None:
            logging.error('please specify --target or --all')
            return
        operations.apply(project, args.env, args.target, args.all, args.deploy)
