import os
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles

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

# Main API router that consolidates all sub-routers
api_router = APIRouter(prefix="/api")

# Include all sub-routers
api_router.include_router(project.router)
api_router.include_router(tables.router)
api_router.include_router(environs.router)
api_router.include_router(refs.router)

# Schema management APIs
api_router.include_router(schemas.router)
api_router.include_router(schema_tables.router)
api_router.include_router(schema_fields.router)
api_router.include_router(schema_indexes.router)
api_router.include_router(schema_views.router)
api_router.include_router(schema_validation.router)

# Mount the API router and static files
app.include_router(api_router)
app.mount('/', StaticFiles(directory=f'{os.path.dirname(__file__)}/static', html=True), name='static')


def run(project: Project, port: int = 5000, host: str = '0.0.0.0'):
    app.state.project = project
    uvicorn.run('dbgear_web.backend:app', port=port, host=host, log_config=None)
