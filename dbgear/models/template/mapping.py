import os
from glob import glob

from ..fileio import load_model
from ..fileio import save_model
from ..fileio import make_folder
from ..fileio import delete_folder
from .. import const

from .data import Mapping
from .utils import get_templates_folder


def get(folder: str, id: str) -> Mapping:
    return load_model(
        f'{get_templates_folder(folder)}/{id}/{const.FNAME_MAPPING}',
        Mapping,
        id=id
    )


def items(folder: str) -> list[Mapping]:
    result = []
    for tmpl in glob(f'{get_templates_folder(folder)}/**/{const.FNAME_MAPPING}'):
        id = tmpl.split('/')[-2]
        config = load_model(tmpl, Mapping, id=id)
        result.append(config)
    return sorted(result, key=lambda x: x.id)


def is_exist(folder: str, id: str) -> bool:
    return os.path.isdir(f'{get_templates_folder(folder)/{id}}')


def save(folder: str, id: str, data: Mapping) -> None:
    make_folder(f'{get_templates_folder(folder)}/{id}')
    save_model(
        f'{get_templates_folder(folder)}/{id}/{const.FNAME_MAPPING}',
        data
    )


def delete(folder: str, id: str) -> None:
    delete_folder(f'{get_templates_folder(folder)}/{id}')
