import uvicorn
import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dbgear.models.project import Project

try:
    # Try relative import first (when run as module)
    from .api import project
    from .api import refs
    from .api import schemas
    from .api import schema_tables
    from .api import schema_columns
    from .api import schema_indexes
    from .api import schema_views
    from .api import schema_validation
    from .api import schema_relations
    from .api import schema_notes
    from .api import schema_triggers
    from .api import schema_column_types
    from .api import schema_dependencies
    from .api import tenants
    from .api import environments
    from .api import mappings
    from .api import datamodels
    from .api import operations
except ImportError:
    # Fallback to absolute import (when run as script)
    from dbgear_web.api import project
    from dbgear_web.api import refs
    from dbgear_web.api import schemas
    from dbgear_web.api import schema_tables
    from dbgear_web.api import schema_columns
    from dbgear_web.api import schema_indexes
    from dbgear_web.api import schema_views
    from dbgear_web.api import schema_validation
    from dbgear_web.api import schema_relations
    from dbgear_web.api import schema_notes
    from dbgear_web.api import schema_triggers
    from dbgear_web.api import schema_column_types
    from dbgear_web.api import schema_dependencies
    from dbgear_web.api import tenants
    from dbgear_web.api import environments
    from dbgear_web.api import mappings
    from dbgear_web.api import datamodels
    from dbgear_web.api import operations

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # Frontend development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and store project in app state
project_path = os.getenv('DBGEAR_PROJECT_PATH', './')
project_instance = Project.load(project_path)
app.state.project = project_instance

# Main API router that consolidates all sub-routers
api_router = APIRouter(prefix="/api")

# Include all sub-routers
api_router.include_router(project.router)
api_router.include_router(refs.router)

# Schema management APIs
api_router.include_router(schemas.router)
api_router.include_router(schema_tables.router)
api_router.include_router(schema_columns.router)
api_router.include_router(schema_indexes.router)
api_router.include_router(schema_views.router)
api_router.include_router(schema_validation.router)
api_router.include_router(schema_relations.router)
api_router.include_router(schema_notes.router)
api_router.include_router(schema_triggers.router)
api_router.include_router(schema_column_types.router)
api_router.include_router(schema_dependencies.router)

# Tenant management APIs
api_router.include_router(tenants.router)

# Environment and deployment APIs
api_router.include_router(environments.router)
api_router.include_router(mappings.router)
api_router.include_router(datamodels.router)
api_router.include_router(operations.router)

# Mount the API router
app.include_router(api_router)


if __name__ == '__main__':
    uvicorn.run('dbgear_web.backend:app', host='0.0.0.0', port=5000, reload=True)
