import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .api import tables
from .api import templates
from .api import environs

from .models.proxy import APIProxy
from .models.response import ProjectInfo

app = FastAPI()

app.mount('/static', StaticFiles(directory='dist', html=True), name='static')
app.include_router(tables.router)
app.include_router(templates.router)
app.include_router(environs.router)


@app.get('/')
def root():
    return RedirectResponse('/static')


@app.get('/project')
def get_project_info():
    api = APIProxy(app)
    return ProjectInfo(
        project_name=api.project_name,
        templates=api.templates,
        environs=api.environs,
        instances=api.instances
    )


def run(project):
    app.state.project = project
    uvicorn.run('dbgear.backend:app', port=5000, log_config=None)
