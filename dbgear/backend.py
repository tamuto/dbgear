import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .api import project
from .api import tables
from .api import environs
from .api import refs

from .models.project import Project

app = FastAPI()

app.mount('/static', StaticFiles(directory=f'{os.path.dirname(__file__)}/web', html=True), name='static')
app.include_router(project.router)
app.include_router(tables.router)
app.include_router(environs.router)
app.include_router(refs.router)


@app.get('/')
def root():
    return RedirectResponse('/static')


def run(project: Project):
    app.state.project = project
    uvicorn.run('dbgear.backend:app', port=5000, host='0.0.0.0', log_config=None)
