from . import engine


def tables(conn, schema):
    sql = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{schema}'"
    return engine.select_all(conn, sql)


def columns(conn, schema, table):
    sql = f'''
        SELECT
        COLUMN_NAME
        , COLUMN_TYPE
        , IS_NULLABLE
        , COLUMN_KEY
        , COLUMN_DEFAULT
        , COLUMN_COMMENT
        FROM information_schema.columns
        WHERE table_schema = '{schema}' AND table_name = '{table}'
        ORDER BY ORDINAL_POSITION
    '''
    return engine.select_all(conn, sql)


def indexes(conn, schema, table):
    sql = f'''
        SELECT
        INDEX_NAME
        , NON_UNIQUE
        , COLUMN_NAME
        , SEQ_IN_INDEX
        FROM information_schema.statistics
        WHERE table_schema = '{schema}' AND table_name = '{table}'
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
    '''
    return engine.select_all(conn, sql)
