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
        'command',
        choices=['serve', 'check', 'apply'],
        help='please specify the command to execute.')
    parser.add_argument(
        '--project',
        default='database',
        help='please specify the folder for the project.')
    parser.add_argument(
        '--env',
        help='target environment for the command.')
    parser.add_argument(
        '--deploy',
        help='target deployment for the command.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    project = Project(args.project)
    project.read_definitions()

    if args.command == 'serve':
        backend.run(project)
    if args.command == 'apply':
        operations.apply(project, args.env, args.deploy)
