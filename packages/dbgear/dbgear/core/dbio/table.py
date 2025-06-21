from . import engine
from .templates.mysql import template_engine

from ..models.schema import Table
from ..models.schema import Column


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


def create(conn, env: str, table: Table):
    # Use template engine for CREATE TABLE
    sql = template_engine.render('mysql_create_table', env=env, table=table)
    engine.execute(conn, sql)

    # Create indexes using template engine
    for idx, index in enumerate(table.indexes):
        # Set loop context for template
        loop_context = type('LoopContext', (), {'index0': idx})()
        sql = template_engine.render(
            'mysql_create_index',
            env=env,
            table=table,
            index=index,
            loop=loop_context)
        engine.execute(conn, sql)


def _col_value(item: dict, column: Column):
    if column.column_name in item:
        if item[column.column_name] is not None and type(item[column.column_name]) is str:
            # 関数定義されている場合には、SQLに関数を埋め込む。
            if '(' in item[column.column_name]:
                return item[column.column_name]
        return f':{column.column_name}'
    return 'NULL'


def insert(conn, env: str, table: Table, items: list[dict]):
    # Filter out generated columns (expression fields) from INSERT
    insertable_columns = [c for c in table.columns if c.expression is None]

    sql = f'INSERT INTO {env}.{table.table_name} ('
    sql += ', '.join([f'`{c.column_name}`' for c in insertable_columns])
    sql += ') VALUES ('
    sql += ', '.join([_col_value(items[0], c) for c in insertable_columns])
    sql += ')'
    engine.execute(conn, sql, items)
    conn.commit()


def backup(conn, env: str, table: Table, ymd: str):
    sql = f'CREATE TABLE {env}.bak_{table.table_name}_{ymd} AS SELECT * FROM {env}.{table.table_name}'
    engine.execute(conn, sql)


def restore(conn, env: str, table: Table, ymd: str):
    sql = f'INSERT IGNORE INTO {env}.{table.table_name} SELECT * FROM {env}.bak_{table.table_name}_{ymd}'
    engine.execute(conn, sql)


def is_exist_backup(conn, env: str, table: Table, ymd: str):
    result = engine.select_one(
        conn,
        '''
        SELECT TABLE_NAME FROM information_schema.tables
        WHERE table_schema = :env and table_name = :table
        ''',
        {'env': env, 'table': f'bak_{table.table_name}_{ymd}'})
    return result is not None
