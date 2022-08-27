import os


def get_CORS():
    return os.environ.get('BACKEND_CORS')


def get_DB_CONN():
    return os.environ.get('BACKEND_MYSQL_CONN')
