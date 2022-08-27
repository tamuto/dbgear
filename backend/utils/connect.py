from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

from . import config

engine = create_engine(
    config.get_DB_CONN(),
    echo=False)

session = scoped_session(
    sessionmaker(
        bind=engine
    )
)


def execute_sql(sql, params=None):
    return session().execute(text(sql), params).mappings()


def read_as_dict(result):
    return [{k: v for k, v in row.items()} for row in result]
