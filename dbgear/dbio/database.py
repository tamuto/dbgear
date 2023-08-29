from . import engine


def is_exist(conn, database):
    result = engine.select_one(conn, 'SHOW DATABASES LIKE :database', {'database': database})
    return result is not None


def create(conn, database, charset='utf8mb4', collation='utf8mb4_unicode_ci'):
    sql = f'CREATE DATABASE {database} DEFAULT CHARACTER SET {charset} COLLATE {collation}'
    engine.execute(conn, sql)


def drop(conn, database):
    sql = f'DROP DATABASE {database}'
    engine.execute(conn, sql)


# def grant(conn, database, user, host, privileges='ALL PRIVILEGES'):
#     sql = f'GRANT {privileges} ON {database}.* TO :user'
#     print(sql)
#     engine.execute(conn, sql, {'user': f'{user}@{host}'})


# def create_user(conn, user, host, password):
#     sql = f"CREATE USER IF NOT EXISTS '{user}'@'{host}' IDENTIFIED BY '{password}'"
#     engine.execute(conn, sql)
