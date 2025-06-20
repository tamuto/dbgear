import yaml
from .definitions import a5sql_mk2

from .models.schema import SchemaManager
from .utils.populate import auto_populate_from_keys


def import_a5sql_mk2(folder: str, filename: str):

    schemas = a5sql_mk2.retrieve(folder, filename, {'MAIN': 'main'})

    with open('test.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(
            schemas.model_dump(exclude_none=True, exclude_defaults=True),
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False)


def load_yaml(filename: str):
    """Load a YAML file and return its content."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    populated_data = auto_populate_from_keys(data, {
        'schemas.$1.name': '$1',
        'schemas.$1.tables.$2.instance': '$1',
        'schemas.$1.tables.$2.table_name': '$2',
        'schemas.$1.views.$2.instance': '$1',
        'schemas.$1.views.$2.view_name': '$2',
    })
    # return populated_data
    return SchemaManager(**populated_data)


if __name__ == "__main__":
    # import_a5sql_mk2('../../etc/test', 'dbgear.a5er')
    # schemas = load_yaml('test.yaml')
    schemas = load_yaml('../../etc/test/schema.yaml')
    print(schemas)
