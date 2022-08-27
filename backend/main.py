import os
import json
from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .utils import config

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


# @app.get('/')
# def root():
#     return RedirectResponse('/static')


# @app.get('/api/hello')
# def hello():
#     return {'message': 'hello'}


# @app.get('/api/sample')
# def get_sample():
#     return execute_sql(
#         'select * from test'
#     ).all()

@app.get('/data/{rest_of_path:path}/{name}')
def test(request: Request, rest_of_path: str, name: str):
    print('****', name)
    data = []
    with os.scandir('./dist/data/' + rest_of_path) as it:
        for entry in it:
            data.append(entry.name)
    return data


@app.put('/data/{rest_of_path:path}/{name}')
def newEntry(rest_of_path: str, name: str, body=Body(...)):
    with open(f'./dist/data/{rest_of_path}/{name}', 'w') as f:
        f.write(json.dumps(body))
    # print(rest_of_path, name, body)
    return 'OK'


@app.delete('/data/{rest_of_path:path}/{name}')
def deleteEntry(rest_of_path: str, name: str):
    os.remove(f'./dist/data/{rest_of_path}/{name}')
    return 'ok'


@app.post('/data/{rest_of_path:path}/{name}')
def updateEntry(rest_of_path: str, name: str, body=Body(...)):
    with open(f'./dist/data/{rest_of_path}/{name}', 'w') as f:
        f.write(json.dumps(body))
    # print(rest_of_path, name, body)
    return 'OK'
