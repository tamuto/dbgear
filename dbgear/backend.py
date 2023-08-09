import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .api import project
from .api import tables
from .api import templates
from .api import environs

from .models.fileio import make_folder
from .models.project import Project
from .models.template.utils import get_templates_folder

app = FastAPI()

app.mount('/static', StaticFiles(directory='dist', html=True), name='static')
app.include_router(project.router)
app.include_router(tables.router)
app.include_router(templates.router)
app.include_router(environs.router)


@app.get('/')
def root():
    return RedirectResponse('/static')


def run(project: Project):
    app.state.project = project

    # 初回起動時のフォルダができていないケースを想定
    make_folder(get_templates_folder(project.folder))

    uvicorn.run('dbgear.backend:app', port=5000, log_config=None)
