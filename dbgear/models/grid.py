from .base import BaseSchema
from uuid import uuid4


class GridColumns(BaseSchema):
    field: str
    type: str
    header_name: str
    width: int
    editable: bool
    items: list = []
    hide: bool = False


def _make_table_grid_column(project, field, settings):
    if field.column_name in settings:
        setting = settings[field.column_name]
        data = project.find_column_setting(setting)
        if data['type'] == 'fixed':
            return GridColumns(
                field=field.column_name,
                type='string',
                header_name=field.display_name,
                width=150,
                editable=False,
                hide=True
            )
        if data['type'] == 'generate':
            return GridColumns(
                field=field.column_name,
                type='string',
                header_name=field.display_name,
                width=150,
                editable=False
            )
        if data['type'] == 'choice':
            return GridColumns(
                field=field.column_name,
                type='singleSelect',
                header_name=field.display_name,
                width=150,
                editable=True,
                items=data['items']
            )
    return GridColumns(
        field=field.column_name,
        type='string',
        header_name=field.display_name,
        width=150,
        editable=True
    )


def make_column_data(project, config):
    if config.layout == 'table':
        columns = []
        for field in config.info.fields:
            col = _make_table_grid_column(project, field, config.settings)
            if col is None:
                continue
            columns.append(col)
        return columns
    if config.layout == 'matrix':
        # TODO
        pass
    if config.layout == 'single':
        # TODO
        pass


def new_data_row(project, config):
    if config.layout == 'table':
        row = {
            'id': uuid4()
        }
        row.update({ field.column_name: '' for field in config.info.fields })
        return row
    # FIXME あとは行追加はないはず。
