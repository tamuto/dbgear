import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

project = None
app = FastAPI()

app.mount('/static', StaticFiles(directory='dist', html=True), name='static')


@app.get('/')
def root():
    return RedirectResponse('/static')


@app.get('/instances')
def get_instances():
    return list(project.definitions.keys())


def run(prj):
    global project
    project = prj
    # uvicorn.run('dbgear.backend:app', port=5000, log_level='info')
    uvicorn.run('dbgear.backend:app', port=5000, log_config=None)
