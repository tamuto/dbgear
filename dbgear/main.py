import logging
from argparse import ArgumentParser

from . import backend
from .models.project import Project


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
        default='etc/dbgear',
        help='please specify the folder for the project.')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    project = Project(args.project)
    project.read_definitions()

    if args.command == 'serve':
        backend.run(project)
