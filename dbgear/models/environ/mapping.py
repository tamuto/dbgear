import os
from glob import glob

from ..fileio import load_model
from ..fileio import save_model
from ..fileio import make_folder
from ..fileio import delete_folder
from ..fileio import get_environ_name
from ..fileio import get_mapping_name

from .data import Mapping


def get(folder: str, id: str) -> Mapping:
    return load_model(
        get_mapping_name(folder, id),
        Mapping,
        id=id
    )


def items(folder: str) -> list[Mapping]:
    result = []
    for tmpl in glob(get_mapping_name(folder, '**')):
        id = tmpl.split('/')[-2]
        config = load_model(tmpl, Mapping, id=id)
        result.append(config)
    return sorted(result, key=lambda x: x.id)


def is_exist(folder: str, id: str) -> bool:
    return os.path.isdir(get_environ_name(folder, id))


def save(folder: str, id: str, data: Mapping) -> None:
    make_folder(get_environ_name(folder, id))
    save_model(
        get_mapping_name(folder, id),
        data
    )


def delete(folder: str, id: str) -> None:
    delete_folder(get_environ_name(folder, id))
