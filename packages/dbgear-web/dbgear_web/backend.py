import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .api import project
from .api import tables
from .api import environs
from .api import refs
from .api import schemas
from .api import schema_tables
from .api import schema_fields
from .api import schema_indexes
from .api import schema_views
from .api import schema_validation

from dbgear.core.models.project import Project

app = FastAPI()

app.mount('/static', StaticFiles(directory=f'{os.path.dirname(__file__)}/static', html=True), name='static')
app.include_router(project.router)
app.include_router(tables.router)
app.include_router(environs.router)
app.include_router(refs.router)

# スキーマ管理API
app.include_router(schemas.router, prefix='/api')
app.include_router(schema_tables.router, prefix='/api')
app.include_router(schema_fields.router, prefix='/api')
app.include_router(schema_indexes.router, prefix='/api')
app.include_router(schema_views.router, prefix='/api')
app.include_router(schema_validation.router, prefix='/api')


@app.get('/')
def root():
    return RedirectResponse('/static')


def run(project: Project, port: int = 5000, host: str = '0.0.0.0'):
    app.state.project = project
    uvicorn.run('dbgear_web.backend:app', port=port, host=host, log_config=None)
