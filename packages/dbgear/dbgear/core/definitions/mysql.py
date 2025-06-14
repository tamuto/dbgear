from ..dbio import engine
from ..dbio import describe

from ..models.schema import Schema
from ..models.schema import Table
from ..models.schema import Field
from ..models.schema import Index


def build_fields(conn, schema, table, primary_key):
    fields = []
    for c in describe.columns(conn, schema, table):
        fields.append(Field(
            column_name=c.COLUMN_NAME,
            display_name=c.COLUMN_NAME,
            column_type=c.COLUMN_TYPE,
            nullable=c.IS_NULLABLE == 'YES',
            primary_key=None if c.COLUMN_NAME not in primary_key else primary_key[c.COLUMN_NAME],
            default_value=c.COLUMN_DEFAULT,
            foreign_key=None,
            comment=c.COLUMN_COMMENT,
        ))
    return fields


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
    schemas = {}
    with engine.get_connection(connect) as conn:
        for instance, schema in mapping.items():
            schemas[schema] = Schema(schema)

            for t in describe.tables(conn, instance):
                primary_key, indexes = build_statistics(conn, instance, t.TABLE_NAME)
                fields = build_fields(conn, instance, t.TABLE_NAME, primary_key)
                schemas[schema].add_table(Table(
                    instance=instance,
                    table_name=t.TABLE_NAME,
                    display_name=t.TABLE_NAME,
                    fields=fields,
                    indexes=list(indexes.values()),
                ))

    return schemas
