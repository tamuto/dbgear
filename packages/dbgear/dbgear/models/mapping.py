import pydantic
import yaml
import pathlib
import os

from .base import BaseSchema


class Mapping(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    environ: str = pydantic.Field(exclude=True)
    name: str = pydantic.Field(exclude=True)
    description: str
    instances: list[str] = []
    deployment: bool = False

    @classmethod
    def load(cls, folder: str, environ: str, name: str):
        with open(f'{folder}/{environ}/{name}/_mapping.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            environ=environ,
            name=name,
            **data
        )


class MappingManager:

    def __init__(self, folder: str, environ: str):
        self.folder = folder
        self.environ = environ

    def __getitem__(self, key: str) -> Mapping:
        return Mapping.load(self.folder, self.environ, key)

    def __iter__(self):
        for path in sorted(pathlib.Path(self.folder).glob(f'{self.environ}/*/_mapping.yaml')):
            name = str(path.parent.relative_to(self.folder))
            yield Mapping.load(self.folder, self.environ, name)

    def add(self, mapping: Mapping) -> None:
        path = os.path.join(self.folder, mapping.environ, mapping.name)
        if os.path.exists(path):
            raise FileExistsError(f'Mapping {mapping.name} already exists in {self.folder}/{mapping.environ}')

        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, '_mapping.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(
                mapping.model_dump(
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
        path = os.path.join(self.folder, self.environ, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f'Mapping {name} does not exist in {self.folder}/{self.environ}')
        files = [f for f in os.listdir(path) if f != '_mapping.yaml']
        if files:
            raise Exception(f'Cannot remove {path}: files other than _mapping.yaml exist')
        os.remove(os.path.join(path, '_mapping.yaml'))
        os.rmdir(path)
