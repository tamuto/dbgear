import os
import shutil
import yaml
from typing import Any
from glob import glob

from ..models.schema import SchemaManager
from ..utils.populate import auto_populate_from_keys
from . import const


def get_environ_name(folder: str, id: str):
    return f'{folder}/{id}'


def get_mapping_name(folder: str, id: str):
    return f'{folder}/{id}/{const.FNAME_MAPPING}'


def get_data_model_name(folder: str, id: str, instance: str, table: str) -> str:
    return f'{folder}/{id}/{instance}@{table}.yaml'


def is_exist_data_model(folder: str, id: str, instance: str, table: str) -> bool:
    return os.path.isfile(get_data_model_name(folder, id, instance, table))


def get_data_dat_name(folder: str, id: str, instance: str, table: str, seg: str | None) -> str:
    if seg is not None:
        return f'{folder}/{id}/{instance}@{table}#{seg}.dat'
    return f'{folder}/{id}/{instance}@{table}.dat'


def save_model(fname: str, model: Any, exclude: list[str] = None) -> None:
    with open(fname, 'w', encoding='utf-8') as f:
        yaml.dump(model.model_dump(exclude=exclude), f, indent=2, allow_unicode=True)


def save_yaml(fname: str, data: object) -> None:
    with open(fname, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, indent=2, allow_unicode=True)


def load_model(fname: str, clazz: Any, **kwargs) -> Any:
    return clazz(**load_yaml(fname), **kwargs)


def load_yaml(fname: str) -> Any:
    with open(fname, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data


def _is_exist_raw_data(folder: str, id: str, ins: str, tbl: str, seg: str | None) -> bool:
    return os.path.isfile(get_data_dat_name(folder, id, ins, tbl, seg))


def load_data(folder: str, id: str, ins: str, tbl: str, seg: str | None) -> Any:
    data = []
    if _is_exist_raw_data(folder, id, ins, tbl, seg):
        data = load_yaml(get_data_dat_name(folder, id, ins, tbl, seg))
    return data


def load_all_data(folder: str, id: str, ins: str, tbl: str) -> Any:
    # セグメントで分かれていても、一つのデータとしてロードする
    data = None
    if _is_exist_raw_data(folder, id, ins, tbl, None):
        return load_yaml(get_data_dat_name(folder, id, ins, tbl, None))

    for f in glob(get_data_dat_name(folder, id, ins, tbl, '*')):
        if data is None:
            data = []
        data.extend(load_yaml(f))

    return data


def make_folder(dirname: str) -> None:
    if not os.path.isdir(dirname):
        os.mkdir(dirname)


def delete_folder(dirname: str) -> None:
    shutil.rmtree(dirname)


def load_schema(filename: str):
    """Load schemas from a YAML file"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    populated_data = auto_populate_from_keys(data, {
        'schemas.$1.name': '$1',
        'schemas.$1.tables.$2.instance': '$1',
        'schemas.$1.tables.$2.table_name': '$2',
        'schemas.$1.views.$2.instance': '$1',
        'schemas.$1.views.$2.view_name': '$2',
    })
    return SchemaManager(**populated_data)


def save_schema(filename: str, schemas: SchemaManager) -> None:
    """Save schemas to a YAML file"""
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(
            schemas.model_dump(
                exclude_none=True,
                exclude_defaults=True
            ),
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False)
