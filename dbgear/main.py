from argparse import ArgumentParser

from . import backend


def execute():
    parser = ArgumentParser(
        prog='dbgear',
        description='database management tools'
    )
    parser.add_argument('--serve', action='store_true')

    args = parser.parse_args()

    if args.serve:
        backend.run()
