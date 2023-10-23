from . import engine

from ..models.schema import Table
from ..models.schema import Field


def is_exist(conn, env: str, table: Table):
    result = engine.select_one(
        conn,
        '''
        SELECT TABLE_NAME FROM information_schema.tables
        WHERE table_schema = :env and table_name = :table
        ''',
        {'env': env, 'table': table.table_name})
    return result is not None


def drop(conn, env: str, table: Table):
    sql = f'DROP TABLE {env}.{table.table_name}'
    engine.execute(conn, sql)


def _column_sql(field: dict):
    sql = f'`{field.column_name}` {field.column_type}'
    if not field.nullable:
        sql += ' NOT NULL'
    if field.default_value is not None:
        sql += f' DEFAULT {field.default_value}'
    return sql


def create(conn, env: str, table: Table):
    pk = sorted(
        [f for f in table.fields if f.primary_key is not None],
        key=lambda x: x.primary_key
    )
    sql = f'CREATE TABLE {env}.{table.table_name} ('
    sql += ', '.join([_column_sql(f) for f in table.fields])
    sql += f', constraint {table.table_name}_PKC primary key '
    sql += '(' + ', '.join([f'`{f.column_name}`' for f in pk]) + ')'
    sql += ')'
    engine.execute(conn, sql)

    for idx, index in enumerate(table.indexes):
        sql = 'CREATE INDEX '
        sql += f'{table.table_name}_IX{idx} ' if index.index_name is None else f'{index.index_name} '
        sql += f'ON {env}.{table.table_name} ('
        sql += ', '.join(index.columns)
        sql += ')'
        engine.execute(conn, sql)


def _col_value(item: dict, field: Field):
    if field.column_name in item:
        if item[field.column_name] is None:
            return 'NULL'
        if type(item[field.column_name]) is str:
            if '(' in item[field.column_name]:
                return item[field.column_name]
        return f':{field.column_name}'
    return 'NULL'


def insert(conn, env: str, table: Table, items: list[dict]):
    sql = f'INSERT INTO {env}.{table.table_name} ('
    sql += ', '.join([f'`{f.column_name}`' for f in table.fields])
    sql += ') VALUES ('
    sql += ', '.join([_col_value(items[0], f) for f in table.fields])
    sql += ')'
    engine.execute(conn, sql, items)
    conn.commit()
