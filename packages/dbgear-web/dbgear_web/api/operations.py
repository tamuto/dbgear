from fastapi import APIRouter, Request, HTTPException
from dbgear.models.environ import EnvironManager
from ..shared.dtos import Result, DeployRequest, DeployPreviewRequest, DeployJobResponse, CreateDatabaseOperationRequest, ApplyDataRequest
from ..shared.helpers import get_project
import uuid
import threading
import time
from typing import Dict


router = APIRouter()

# In-memory job storage (in production, you'd use Redis or database)
deploy_jobs: Dict[str, dict] = {}


def execute_deploy_job(job_id: str, data: DeployRequest, project_folder: str):
    """Background task to execute deployment"""
    try:
        deploy_jobs[job_id]['status'] = 'running'
        deploy_jobs[job_id]['progress'] = 0.1

        executed_operations = []

        # Prepare deployment parameters
        # environment = data.environment
        mapping = data.mapping
        schemas = data.schemas or []
        tables = data.tables or []

        deploy_jobs[job_id]['progress'] = 0.3
        deploy_jobs[job_id]['message'] = 'Preparing deployment...'

        # Execute deployment operations
        # This is a simplified implementation - in reality you'd call the actual CLI operations
        try:
            # Simulate database operations
            if data.drop_existing:
                executed_operations.append(f"DROP DATABASE IF EXISTS for {mapping}")
                deploy_jobs[job_id]['progress'] = 0.4

            executed_operations.append(f"CREATE DATABASE for {mapping}")
            deploy_jobs[job_id]['progress'] = 0.5

            # Apply schemas
            for schema_name in schemas:
                executed_operations.append(f"CREATE SCHEMA {schema_name}")
                deploy_jobs[job_id]['progress'] += 0.1

            # Apply tables
            for table_name in tables:
                executed_operations.append(f"CREATE TABLE {table_name}")
                deploy_jobs[job_id]['progress'] += 0.05

            # Apply data if requested
            if data.apply_data:
                executed_operations.append(f"INSERT DATA for {mapping}")
                deploy_jobs[job_id]['progress'] = 0.9

            deploy_jobs[job_id]['status'] = 'completed'
            deploy_jobs[job_id]['progress'] = 1.0
            deploy_jobs[job_id]['message'] = 'Deployment completed successfully'
            deploy_jobs[job_id]['executed_operations'] = executed_operations

        except Exception as e:
            deploy_jobs[job_id]['status'] = 'failed'
            deploy_jobs[job_id]['message'] = f"Deployment failed: {str(e)}"
            deploy_jobs[job_id]['executed_operations'] = executed_operations

    except Exception as e:
        deploy_jobs[job_id]['status'] = 'failed'
        deploy_jobs[job_id]['message'] = str(e)


@router.post('/deploy')
def deploy_schema(data: DeployRequest, request: Request):
    """Deploy schema to database"""
    try:
        project = get_project(request)

        # Validate environment and mapping exist
        manager = EnvironManager(project.folder)
        if data.environment not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        environ = manager[data.environment]
        if not hasattr(environ, 'mappings') or data.mapping not in environ.mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")

        # Create deployment job
        job_id = str(uuid.uuid4())
        deploy_jobs[job_id] = {
            'status': 'pending',
            'progress': 0.0,
            'message': None,
            'executed_operations': [],
            'created_at': time.time()
        }

        # Start background task
        thread = threading.Thread(target=execute_deploy_job, args=(job_id, data, project.folder))
        thread.daemon = True
        thread.start()

        return Result(data=DeployJobResponse(
            job_id=job_id,
            status='pending',
            progress=0.0,
            message='Deployment queued'
        ))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {e}")


@router.post('/deploy/preview')
def preview_deployment(data: DeployPreviewRequest, request: Request):
    """Preview deployment changes without executing"""
    try:
        project = get_project(request)

        # Validate environment and mapping exist
        manager = EnvironManager(project.folder)
        if data.environment not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        environ = manager[data.environment]
        if not hasattr(environ, 'mappings') or data.mapping not in environ.mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")

        # Generate preview of operations that would be executed
        preview_operations = []

        # Database operations
        preview_operations.append({
            'type': 'database',
            'operation': 'CREATE',
            'target': data.mapping,
            'description': f"Create database for mapping '{data.mapping}'"
        })

        # Schema operations
        schemas = data.schemas or []
        for schema_name in schemas:
            preview_operations.append({
                'type': 'schema',
                'operation': 'CREATE',
                'target': schema_name,
                'description': f"Create schema '{schema_name}'"
            })

        # Table operations
        tables = data.tables or []
        for table_name in tables:
            preview_operations.append({
                'type': 'table',
                'operation': 'CREATE',
                'target': table_name,
                'description': f"Create table '{table_name}'"
            })

        preview = {
            'environment': data.environment,
            'mapping': data.mapping,
            'operations': preview_operations,
            'operation_count': len(preview_operations),
            'estimated_duration': f"{len(preview_operations) * 2} seconds"
        }

        return Result(data=preview)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {e}")


@router.get('/deploy/status/{job_id}')
def get_deploy_status(job_id: str, request: Request):
    """Get deployment job status"""
    try:
        if job_id not in deploy_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job = deploy_jobs[job_id]

        return Result(data=DeployJobResponse(
            job_id=job_id,
            status=job['status'],
            progress=job['progress'],
            message=job['message'],
            executed_operations=job.get('executed_operations', [])
        ))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/operations/create-database')
def create_database(data: CreateDatabaseOperationRequest, request: Request):
    """Create a database"""
    try:
        project = get_project(request)

        # Validate environment exists
        manager = EnvironManager(project.folder)
        if data.environment not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        # This would typically call the actual database creation operation
        # For now, we'll simulate it
        result = {
            'environment': data.environment,
            'database_name': data.database_name,
            'status': 'created',
            'message': f"Database '{data.database_name}' created successfully"
        }

        return Result(data=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database creation failed: {e}")


@router.post('/operations/drop-database')
def drop_database(data: CreateDatabaseOperationRequest, request: Request):
    """Drop a database"""
    try:
        project = get_project(request)

        # Validate environment exists
        manager = EnvironManager(project.folder)
        if data.environment not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        # This would typically call the actual database drop operation
        # For now, we'll simulate it
        result = {
            'environment': data.environment,
            'database_name': data.database_name,
            'status': 'dropped',
            'message': f"Database '{data.database_name}' dropped successfully"
        }

        return Result(data=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database drop failed: {e}")


@router.post('/operations/apply-data')
def apply_data_operation(data: ApplyDataRequest, request: Request):
    """Apply data to database"""
    try:
        project = get_project(request)

        # Validate environment and mapping exist
        manager = EnvironManager(project.folder)
        if data.environment not in manager:
            raise HTTPException(status_code=404, detail="Environment not found")

        environ = manager[data.environment]
        if not hasattr(environ, 'mappings') or data.mapping not in environ.mappings:
            raise HTTPException(status_code=404, detail="Mapping not found")

        # This would typically call the actual data application operation
        # For now, we'll simulate it
        applied_tables = []

        schemas = data.schemas or []
        tables = data.tables or []

        # Simulate applying data
        for schema_name in schemas:
            for table_name in tables:
                applied_tables.append(f"{schema_name}.{table_name}")

        result = {
            'environment': data.environment,
            'mapping': data.mapping,
            'applied_tables': applied_tables,
            'truncate_existing': data.truncate_existing,
            'status': 'completed',
            'message': f"Data applied to {len(applied_tables)} tables"
        }

        return Result(data=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data application failed: {e}")


@router.get('/deploy/jobs')
def get_deploy_jobs(request: Request):
    """Get all deployment jobs"""
    try:
        jobs = []
        for job_id, job_data in deploy_jobs.items():
            jobs.append(DeployJobResponse(
                job_id=job_id,
                status=job_data['status'],
                progress=job_data['progress'],
                message=job_data['message'],
                executed_operations=job_data.get('executed_operations', [])
            ))

        return Result(data=jobs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/deploy/jobs/{job_id}')
def delete_deploy_job(job_id: str, request: Request):
    """Delete deployment job (cleanup)"""
    try:
        if job_id not in deploy_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        del deploy_jobs[job_id]

        return Result()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
