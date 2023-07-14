import yaml
import os
from glob import glob

from .base import BaseSchema


class TemplateConfig(BaseSchema):
    id: str
    name: str
    instances: list = []


class DataFilename(BaseSchema):
    instance: str
    table_name: str
    display_name: str


class Template:

    def __init__(self, project, folder):
        self.project = project
        self.folder = folder
        self.templates = []

    def _get_templates_folder(self):
        return f'{self.folder}/templates'

    def _get_template(self, id):
        return next(iter([t for t in self.templates if t.id == id]), None)

    def setup(self):
        if not os.path.isdir(self._get_templates_folder()):
            os.mkdir(self._get_templates_folder())

    def is_exist_template(self, id):
        return os.path.isdir(f'{self._get_templates_folder()}/{id}')

    def create_template(self, id, name, instances):
        path = f'{self._get_templates_folder()}/{id}'

        os.mkdir(path)
        os.mkdir(f'{path}/data')

        with open(f'{path}/mapping.yaml', 'w', encoding='utf-8') as f:
            config = TemplateConfig(
                id=id,
                name=name,
                instances=instances
            )
            yaml.dump(config.model_dump(), f, indent=2, allow_unicode=True)

    def read_templates(self):
        for tmpl in glob(f'{self._get_templates_folder()}/**/mapping.yaml'):
            with open(tmpl, 'r', encoding='utf-8') as f:
                config = TemplateConfig(
                    **yaml.safe_load(f)
                )
            self.templates.append(config)

    def scan_data_folder(self, id):
        return glob(f'{self._get_templates_folder()}/{id}/data/*.yaml')

    # def scan_data_list(self, id):
    #     def make_tuple(path):
    #         fname = os.path.splitext(os.path.basename(path))[0]
    #         f = fname.split('@')
    #         return (f[0], f[1])

    #     return [make_tuple(p) for p in self.scan_data_folder(id)]

    def is_exist_data(self, id, instance, table):
        fname = f'{self._get_templates_folder()}/{id}/data/{instance}@{table}.yaml'
        return os.path.isfile(fname)

    def listup_for_init(self, id):
        config = self._get_template(id)
        tables = []
        for ins in config.instances:
            tables.extend([
                DataFilename(instance=ins, table_name=t.table_name, display_name=t.display_name)
                for t in self.project.definitions[ins].tables.values()
                if not self.is_exist_data(id, ins, t.table_name)
            ])
        return sorted(tables, key=lambda x: f'{x.instance}@{x.table_name}')
