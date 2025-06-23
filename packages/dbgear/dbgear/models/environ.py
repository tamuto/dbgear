import pydantic
import pathlib
import os
import yaml

from .base import BaseSchema
from .schema import SchemaManager


class Environ(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    name: str = pydantic.Field(exclude=True)
    description: str

    _schemas: SchemaManager | None = None

    @classmethod
    def load(cls, folder: str, name: str) -> None:
        with open(f'{folder}/{name}/environ.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            name=name,
            **data)

    @property
    def schemas(self) -> SchemaManager:
        if self._schemas is None:
            self._schemas = SchemaManager.load(f'{self.folder}/{self.name}/schema.yaml')
        return self._schemas


class EnvironManager:

    def __init__(self, folder: str):
        self.folder = folder

    def __getitem__(self, key: str) -> Environ:
        path = os.path.join(self.folder, key, 'environ.yaml')
        if os.path.isfile(path):
            return Environ.load(path)
        raise KeyError(f'Environment {key} does not exist in {self.folder}')

    def __iter__(self):
        for path in sorted(pathlib.Path(self.folder).glob('*/environ.yaml')):
            name = str(path.parent.relative_to(self.folder))
            yield Environ.load(self.folder, name)

    def add(self, name: str, environ: Environ) -> None:
        path = os.path.join(self.folder, name)
        if os.path.exists(path):
            raise FileExistsError(f'Environment {name} already exists in {self.folder}')

        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, 'environ.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(environ.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True
                ),
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False)

    def remove(self, name: str) -> None:
        path = os.path.join(self.folder, name)
        if not os.path.exists(path):
            raise KeyError(f'Environment {name} does not exist in {self.folder}')
        files = [f for f in os.listdir(path) if f != 'environ.yaml']
        if files:
            raise Exception(f'Cannot remove {path}: files other than environ.yaml exist')
        os.remove(os.path.join(path, 'environ.yaml'))
        os.rmdir(path)


if __name__ == '__main__':
    # Example usage
    envs = EnvironManager('../../etc/test')
    for environ in envs:
        print(environ)

    # envs.remove('env2')
