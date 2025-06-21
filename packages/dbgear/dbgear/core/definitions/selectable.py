from ..models.schema import Schema
from ..models.schema import Table
from ..models.schema import Column


def retrieve(folder, prefix, items, **kwargs):
    schema = Schema(name=prefix)

    for key, val in items.items():
        table = Table(instance=prefix, table_name=key, display_name=val)
        schema.add_table(table)

        table.add_column(Column(
            column_name='value',
            display_name='Value',
            column_type='varchar',
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None
        ))
        table.add_column(Column(
            column_name='caption',
            display_name='Caption',
            column_type='varchar',
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None
        ))
    return {
        prefix: schema
    }
