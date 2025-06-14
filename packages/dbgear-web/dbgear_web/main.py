import logging
from argparse import ArgumentParser

from dbgear.core.models.project import Project
from . import backend


def execute():
    parser = ArgumentParser(
        prog='dbgear-web',
        description='database management tools - Web interface'
    )
    parser.add_argument(
        '--project',
        default='database',
        help='please specify the folder for the project.')
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='port number for web server (default: 5000)')
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='host address for web server (default: 0.0.0.0)')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    project = Project(args.project)
    project.read_definitions()

    backend.run(project, port=args.port, host=args.host)


if __name__ == '__main__':
    execute()