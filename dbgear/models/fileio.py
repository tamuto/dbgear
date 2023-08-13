import os
import shutil
import yaml
from typing import Any

from . import const


def get_environ_name(folder: str, id: str):
    return f'{folder}/{id}'


def get_mapping_name(folder: str, id: str):
    return f'{folder}/{id}/{const.FNAME_MAPPING}'


def get_data_model_name(folder: str, id: str, instance: str, table: str) -> str:
    return f'{folder}/{id}/{instance}@{table}.yaml'


def get_data_dat_name(folder: str, id: str, instance: str, table: str) -> str:
    return f'{folder}/{id}/{instance}@{table}.dat'


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


def _is_exist_raw_data(folder: str, id: str, ins: str, tbl: str) -> bool:
    return os.path.isfile(get_data_dat_name(folder, id, ins, tbl))


def load_data(folder: str, id: str, ins: str, tbl: str, none: bool = False) -> Any:
    data = None if none else []
    if _is_exist_raw_data(folder, id, ins, tbl):
        data = load_yaml(get_data_dat_name(folder, id, ins, tbl))
    return data


def make_folder(dirname: str) -> None:
    if not os.path.isdir(dirname):
        os.mkdir(dirname)


def delete_folder(dirname: str) -> None:
    shutil.rmtree(dirname)
