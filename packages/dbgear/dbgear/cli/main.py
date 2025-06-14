import logging
from argparse import ArgumentParser

from ..core.models.project import Project
from ..core import operations


def execute():
    parser = ArgumentParser(
        prog='dbgear-cli',
        description='database management tools - CLI interface'
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
        '--target',
        help='target table.')
    apply_parser.add_argument(
        '--all',
        choices=['drop', 'delta'],
        help='apply all tables. Specify "drop" to drop database before applying, or "delta" to apply only the changes since the last deployment.'
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    if args.command is None:
        parser.print_help()
        return

    project = Project(args.project)
    project.read_definitions()

    if args.command == 'apply':
        if not args.all and args.target is None:
            logging.error('please specify --target or --all')
            return
        operations.apply(project, args.env, args.target, args.all, args.deploy)


if __name__ == '__main__':
    execute()