import yaml
import os

from logging import getLogger
from glob import glob
from importlib import import_module

from .template import Template
from .environ import Environ


class Project:
    logger = getLogger('project')

    def __init__(self, folder):
        self.folder = folder
        self.config = {}
        self.definitions = {}
        self.template = Template(self, folder)
        self.environ = Environ(self, folder)

    def setup(self):
        self.template.setup()
        self.environ.setup()

    def read_project(self):
        with open(f'{self.folder}/project.yaml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.template.read_templates()
        self.environ.read_environs()

    def read_definitions(self):
        for items in self.config['definitions']:
            self.logger.info(f"definition: {items['filename']}, {items['type']}")
            module = import_module(f'.{items["type"]}', 'dbgear.definitions')
            result = module.retrieve(self.folder, **items)

            self.definitions.update(result)
