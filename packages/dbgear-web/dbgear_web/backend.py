import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .api import project
from .api import tables
from .api import environs
from .api import refs

from dbgear.core.models.project import Project

app = FastAPI()

app.mount('/static', StaticFiles(directory=f'{os.path.dirname(__file__)}/static', html=True), name='static')
app.include_router(project.router)
app.include_router(tables.router)
app.include_router(environs.router)
app.include_router(refs.router)


@app.get('/')
def root():
    return RedirectResponse('/static')


def run(project: Project, port: int = 5000, host: str = '0.0.0.0'):
    app.state.project = project
    uvicorn.run('dbgear_web.backend:app', port=port, host=host, log_config=None)
