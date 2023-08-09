import os
import shutil
import yaml
from typing import Any


def save_model(fname: str, model: Any) -> None:
    with open(fname, 'w', encoding='utf-8') as f:
        yaml.dump(model.model_dump(), f, indent=2, allow_unicode=True)


def save_yaml(fname: str, data: object) -> None:
    with open(fname, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, indent=2, allow_unicode=True)


def load_model(fname: str, clazz: Any, **kwargs) -> Any:
    return clazz(**load_yaml(fname), **kwargs)


def load_yaml(fname: str) -> Any:
    with open(fname, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data


def make_folder(dirname: str) -> None:
    if not os.path.isdir(dirname):
        os.mkdir(dirname)


def delete_folder(dirname: str) -> None:
    shutil.rmtree(dirname)
