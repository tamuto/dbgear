import yaml
import os
from typing import Dict
from glob import glob

from .base import BaseSchema
from .schema import Table
from .grid import GridColumns
from . import grid

class TemplateConfig(BaseSchema):
    id: str
    name: str
    instances: list = []


class DataFilename(BaseSchema):
    instance: str
    table_name: str
    display_name: str


class TemplateDataConfig(BaseSchema):
    layout: str
    settings: Dict[str, str]
    # TODO layoutの情報のパラメータ追加する


class TemplateDataInfo(TemplateDataConfig):
    instance: str | None = None
    info: Table | None = None
    grid_columns: list = []
    grid_rows: list = []
    # TODO データそのもの


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
        self.templates.clear()
        for tmpl in glob(f'{self._get_templates_folder()}/**/mapping.yaml'):
            with open(tmpl, 'r', encoding='utf-8') as f:
                config = TemplateConfig(
                    **yaml.safe_load(f)
                )
            self.templates.append(config)

    def _make_data_filename(self, id, instance, table):
        return f'{self._get_templates_folder()}/{id}/data/{instance}@{table}.yaml'

    def _make_raw_filename(self, id, instance, table):
        return f'{self._get_templates_folder()}/{id}/data/{instance}@{table}.dat'

    def is_exist_data(self, id, instance, table):
        fname = self._make_data_filename(id, instance, table)
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

    def listup_data(self, id):
        config = self._get_template(id)
        tables = []
        for ins in config.instances:
            tables.extend([
                DataFilename(instance=ins, table_name=t.table_name, display_name=t.display_name)
                for t in self.project.definitions[ins].tables.values()
                if self.is_exist_data(id, ins, t.table_name)
            ])
        return sorted(tables, key=lambda x: f'{x.instance}@{x.table_name}')

    def create_template_data(self, id, instance, table_name, layout, settings):
        fname = self._make_data_filename(id, instance, table_name)
        with open(fname, 'w', encoding='utf-8') as f:
            config = TemplateDataConfig(
                layout=layout,
                settings=settings
            )
            yaml.dump(config.model_dump(), f, indent=2, allow_unicode=True)

    def _read_template_data_config(self, id, instance, table_name):
        fname = self._make_data_filename(id, instance, table_name)
        with open(fname, 'r', encoding='utf-8') as f:
            config = TemplateDataInfo(
                **yaml.safe_load(f)
            )
        config.instance = instance
        config.info = self.project.definitions[instance].get_table(table_name)
        return config

    def read_template_data(self, id, instance, table_name):
        config = self._read_template_data_config(id, instance, table_name)
        config.grid_columns = grid.make_column_data(self.project, config)
        config.grid_rows = self.read_raw_data(id, instance, table_name)
        return config

    def build_new_data_row(self, id, instance, table_name):
        config = self._read_template_data_config(id, instance, table_name)
        row = grid.new_data_row(self.project, config)
        return row

    def read_raw_data(self, id, instance, table_name):
        fname = self._make_raw_filename(id, instance, table_name)
        if not os.path.isfile(fname):
            return []
        with open(fname, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data

    def update_raw_data(self, id, instance, table_name, data):
        fname = self._make_raw_filename(id, instance, table_name)
        with open(fname, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, indent=2, allow_unicode=True)
