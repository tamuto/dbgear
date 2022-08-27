#!/bin/bash
export BACKEND_MYSQL_CONN="mysql+pymysql://root:password@denv.host/test?charset=utf8"
export BACKEND_CORS=1
poetry run flake8 backend
if [ $? -ne 0 ] ; then
    exit 1
fi
poetry run python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
