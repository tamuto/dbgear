from ..dbio import engine
from ..dbio import describe

from ..models.schema import SchemaManager
from ..models.schema import Schema
from ..models.schema import Table
from ..models.schema import Column
from ..models.schema import Index


def build_columns(conn, schema, table, primary_key):
    columns = []
    for c in describe.columns(conn, schema, table):
        columns.append(Column(
            column_name=c.COLUMN_NAME,
            display_name=c.COLUMN_NAME,
            column_type=c.COLUMN_TYPE,
            nullable=c.IS_NULLABLE == 'YES',
            primary_key=None if c.COLUMN_NAME not in primary_key else primary_key[c.COLUMN_NAME],
            default_value=c.COLUMN_DEFAULT,
            foreign_key=None,
        ))
    return columns


def build_statistics(conn, schema, table):
    primary_key = {}
    indexes = {}
    for i in describe.indexes(conn, schema, table):
        if i.INDEX_NAME == 'PRIMARY':
            primary_key[i.COLUMN_NAME] = i.SEQ_IN_INDEX
        else:
            if i.INDEX_NAME in indexes:
                indexes[i.INDEX_NAME].columns.append(i.COLUMN_NAME)
            else:
                indexes[i.INDEX_NAME] = Index(
                    index_name=i.INDEX_NAME,
                    columns=[i.COLUMN_NAME],
                )
    return primary_key, indexes


def retrieve(folder, connect, mapping, **kwargs):
    schemas = SchemaManager()
    with engine.get_connection(connect) as conn:
        for instance, schema in mapping.items():
            schemas.add_schema(Schema(name=schema))

            for t in describe.tables(conn, instance):
                primary_key, indexes = build_statistics(conn, instance, t.TABLE_NAME)
                columns = build_columns(conn, instance, t.TABLE_NAME, primary_key)
                schemas.get_schema(schema).add_table(Table(
                    instance=instance,
                    table_name=t.TABLE_NAME,
                    display_name=t.TABLE_NAME,
                    columns=columns,
                    indexes=list(indexes.values()),
                ))

    return schemas
