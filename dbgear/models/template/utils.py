def get_templates_folder(folder: str) -> str:
    return f'{folder}/templates'


def get_data_yamlname(folder: str, id: str, instance: str, table: str) -> str:
    return f'{get_templates_folder(folder)}/{id}/{instance}@{table}.yaml'


def get_data_rawname(folder: str, id: str, instance: str, table: str) -> str:
    return f'{get_templates_folder(folder)}/{id}/{instance}@{table}.dat'
