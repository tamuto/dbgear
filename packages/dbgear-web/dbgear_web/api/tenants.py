from fastapi import APIRouter, Request, HTTPException
from dbgear.models.tenant import TenantConfig, TenantRegistry, DatabaseInfo
from ..shared.dtos import Result, CreateTenantRequest, UpdateTenantRequest, CreateDatabaseRequest
from ..shared.helpers import get_project


router = APIRouter()


def get_tenant_registry(request: Request) -> TenantRegistry:
    """Get or create tenant registry from project"""
    project = get_project(request)
    
    if not hasattr(project, 'tenant_registry'):
        project.tenant_registry = TenantRegistry()
    
    return project.tenant_registry


@router.get('/tenants')
def get_tenants(request: Request):
    """Get all tenants"""
    try:
        registry = get_tenant_registry(request)
        return Result(data=list(registry))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/tenants/{tenant_id}')
def get_tenant(tenant_id: str, request: Request):
    """Get a specific tenant"""
    try:
        registry = get_tenant_registry(request)
        
        if tenant_id not in registry:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant = registry[tenant_id]
        return Result(data=tenant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/tenants')
def create_tenant(data: CreateTenantRequest, request: Request):
    """Create a new tenant"""
    try:
        registry = get_tenant_registry(request)
        
        # Check if tenant already exists
        if data.tenant_id in registry:
            raise HTTPException(status_code=409, detail=f"Tenant '{data.tenant_id}' already exists")
        
        # Create tenant config
        tenant = TenantConfig(
            tenant_id=data.tenant_id,
            name=data.name,
            description=data.description,
            config=data.config or {},
            databases={}
        )
        
        # Add to registry
        registry.add(data.tenant_id, tenant)
        
        # Save (assuming the registry has a save method or is auto-saved)
        # Note: This might need adjustment based on actual TenantRegistry implementation
        
        return Result(data=tenant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/tenants/{tenant_id}')
def update_tenant(tenant_id: str, data: UpdateTenantRequest, request: Request):
    """Update an existing tenant"""
    try:
        registry = get_tenant_registry(request)
        
        if tenant_id not in registry:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant = registry[tenant_id]
        
        # Update tenant attributes
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        
        # Save registry
        # Note: This might need adjustment based on actual TenantRegistry implementation
        
        return Result(data=tenant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/tenants/{tenant_id}')
def delete_tenant(tenant_id: str, request: Request):
    """Delete a tenant"""
    try:
        registry = get_tenant_registry(request)
        
        if tenant_id not in registry:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Remove from registry
        registry.remove(tenant_id)
        
        # Save registry
        # Note: This might need adjustment based on actual TenantRegistry implementation
        
        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/tenants/{tenant_id}/databases')
def get_tenant_databases(tenant_id: str, request: Request):
    """Get all databases for a tenant"""
    try:
        registry = get_tenant_registry(request)
        
        if tenant_id not in registry:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant = registry[tenant_id]
        
        if hasattr(tenant, 'databases'):
            return Result(data=list(tenant.databases.values()))
        else:
            return Result(data=[])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/tenants/{tenant_id}/databases/{database_name}')
def get_tenant_database(tenant_id: str, database_name: str, request: Request):
    """Get a specific database for a tenant"""
    try:
        registry = get_tenant_registry(request)
        
        if tenant_id not in registry:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant = registry[tenant_id]
        
        if not hasattr(tenant, 'databases') or database_name not in tenant.databases:
            raise HTTPException(status_code=404, detail="Database not found")
        
        database = tenant.databases[database_name]
        return Result(data=database)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/tenants/{tenant_id}/databases')
def create_tenant_database(tenant_id: str, data: CreateDatabaseRequest, request: Request):
    """Create a new database for a tenant"""
    try:
        registry = get_tenant_registry(request)
        
        if tenant_id not in registry:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant = registry[tenant_id]
        
        # Check if database already exists
        if hasattr(tenant, 'databases') and data.database_name in tenant.databases:
            raise HTTPException(status_code=409, detail=f"Database '{data.database_name}' already exists")
        
        # Create database info
        database = DatabaseInfo(
            database_name=data.database_name,
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password,
            connection_params=data.connection_params or {}
        )
        
        # Add to tenant databases
        if not hasattr(tenant, 'databases'):
            tenant.databases = {}
        tenant.databases[data.database_name] = database
        
        # Save registry
        # Note: This might need adjustment based on actual TenantRegistry implementation
        
        return Result(data=database)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/tenants/{tenant_id}/databases/{database_name}')
def delete_tenant_database(tenant_id: str, database_name: str, request: Request):
    """Delete a database from a tenant"""
    try:
        registry = get_tenant_registry(request)
        
        if tenant_id not in registry:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant = registry[tenant_id]
        
        if not hasattr(tenant, 'databases') or database_name not in tenant.databases:
            raise HTTPException(status_code=404, detail="Database not found")
        
        # Remove database
        del tenant.databases[database_name]
        
        # Save registry
        # Note: This might need adjustment based on actual TenantRegistry implementation
        
        return Result()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))