import yaml
import os

from logging import getLogger
from glob import glob
from importlib import import_module

from .models.settings import Settings


class Project:
    logger = getLogger('project')

    def __init__(self, folder):
        self.folder = folder
        self.config = {}
        self.templates = []
        self.environs = []
        self.definitions = {}

    def setup(self):
        if not os.path.isdir(self._get_templates_folder()):
            os.mkdir(self._get_templates_folder())
        if not os.path.isdir(self._get_environs_folder()):
            os.mkdir(self._get_environs_folder())

    def _get_templates_folder(self):
        return f'{self.folder}/templates'

    def _get_environs_folder(self):
        return f'{self.folder}/environs'

    def read_project(self):
        with open(f'{self.folder}/project.yaml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        for tmpl in glob(f'{self._get_templates_folder()}/**/mapping.yaml'):
            with open(tmpl, 'r', encoding='utf-8') as f:
                settings = Settings(**yaml.safe_load(f))
            self.templates.append(settings)

        for environ in glob(f'{self._get_environs_folder()}/**/mapping.yaml'):
            print(environ)

    def is_exist_template(self, id):
        return os.path.isdir(f'{self._get_templates_folder()}/{id}')

    def create_template(self, id, name, instances):
        os.mkdir(f'{self._get_templates_folder()}/{id}')
        os.mkdir(f'{self._get_templates_folder()}/{id}/data')
        os.mkdir(f'{self._get_templates_folder()}/{id}/layout')

        with open(f'{self._get_templates_folder()}/{id}/mapping.yaml', 'w', encoding='utf-8') as f:
            settings = Settings(
                id=id,
                name=name,
                instances=instances
            )
            yaml.dump(settings.model_dump(), f, indent=2, allow_unicode=True)

    def read_definitions(self):
        for items in self.config['definitions']:
            self.logger.info(f"definition: {items['filename']}, {items['type']}")
            module = import_module(f'.{items["type"]}', 'dbgear.definitions')
            result = module.retrieve(self.folder, **items)

            self.definitions.update(result)
