import os

from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

from dbgear.models.project import Project

from .api import project
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

# Environment APIs
api_router.include_router(environments.router)
api_router.include_router(mappings.router)
api_router.include_router(datamodels.router)

# Mount the API router
app.include_router(api_router)
