from logging import getLogger
from importlib import import_module

from .base import BaseSchema
from .schema import Schema
from .fileio import load_yaml


class Binding(BaseSchema):
    type: str
    value: str


class Project:
    logger = getLogger('project')

    def __init__(self, folder: str):
        self.folder = folder

        data = load_yaml(f'{folder}/project.yaml')
        self.project_name = data['project_name']
        self.description = data['description']
        self._rules = data['rules']
        self._definitions = data['definitions']
        self._bindings = {k: Binding(**v) for k, v in data['bindings'].items()}
        self._schemas = {}
        self.deployments = data['deployments']

    @property
    def bindings(self) -> dict[str, Binding]:
        return self._bindings

    @property
    def rules(self) -> dict[str, str]:
        return self._rules

    @property
    def schemas(self) -> dict[str, Schema]:
        return self._schemas

    @property
    def instances(self) -> list[str]:
        return list(self._schemas.keys())

    def read_definitions(self) -> None:
        for items in self._definitions:
            self.logger.info(f"definition: {items['type']}")
            module = import_module(f'.{items["type"]}', 'dbgear.definitions')
            result = module.retrieve(self.folder, **items)

            self._schemas.update(result)


def project(request) -> Project:
    return request.app.state.project
