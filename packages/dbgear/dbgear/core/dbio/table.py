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


def _column_sql(field: Field):
    sql = f'`{field.column_name}` {field.column_type}'
    
    # Add character set and collation for string columns
    if field.charset is not None:
        sql += f' CHARACTER SET {field.charset}'
    if field.collation is not None:
        sql += f' COLLATE {field.collation}'
    
    # Add nullable constraint
    if not field.nullable:
        sql += ' NOT NULL'
    
    # Add AUTO_INCREMENT
    if field.auto_increment:
        sql += ' AUTO_INCREMENT'
    
    # Add generated column expression or default value
    if field.expression is not None:
        storage_type = 'STORED' if field.stored else 'VIRTUAL'
        sql += f' GENERATED ALWAYS AS ({field.expression}) {storage_type}'
    elif field.default_value is not None:
        sql += f' DEFAULT {field.default_value}'
    
    # Add comment
    if field.comment is not None:
        # Escape single quotes in comment
        escaped_comment = field.comment.replace("'", "''")
        sql += f" COMMENT '{escaped_comment}'"
    
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
        if item[field.column_name] is not None and type(item[field.column_name]) is str:
            # 関数定義されている場合には、SQLに関数を埋め込む。
            if '(' in item[field.column_name]:
                return item[field.column_name]
        return f':{field.column_name}'
    return 'NULL'


def insert(conn, env: str, table: Table, items: list[dict]):
    # Filter out generated columns (expression fields) from INSERT
    insertable_fields = [f for f in table.fields if f.expression is None]
    
    sql = f'INSERT INTO {env}.{table.table_name} ('
    sql += ', '.join([f'`{f.column_name}`' for f in insertable_fields])
    sql += ') VALUES ('
    sql += ', '.join([_col_value(items[0], f) for f in insertable_fields])
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
