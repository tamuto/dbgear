from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .utils import config
from .utils.connect import execute_sql

app = FastAPI()

app.mount('/static', StaticFiles(directory='dist', html=True), name='static')

if config.get_CORS() == '1':
    origins = ['http://localhost:8080']

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
        allow_headers=['*']
    )


@app.get('/')
def root():
    return RedirectResponse('/static')


@app.get('/api/hello')
def hello():
    return {'message': 'hello'}


@app.get('/api/sample')
def get_sample():
    return execute_sql(
        'select * from test'
    ).all()
