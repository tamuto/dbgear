from fastapi import APIRouter, Request, HTTPException
from ..shared.helpers import get_project
from dbgear.models.schema import SchemaManager
from ..shared.dtos import Result, CreateSchemaRequest

router = APIRouter()


@router.get('/schemas')
def get_schemas(request: Request) -> Result:
    """スキーマ一覧を取得"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))
        schemas = manager.get_schemas()
        return Result(data=list(schemas.keys()))
    except Exception as e:
        print(f"Error retrieving schemas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas')
def create_schema(request: Request, schema_request: CreateSchemaRequest) -> Result:
    """新規スキーマを作成"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if manager.schema_exists(schema_request.schema_name):
            raise HTTPException(status_code=400, detail=f"Schema '{schema_request.schema_name}' already exists")

        manager.create_schema(schema_request.schema_name)
        manager.save()

        return Result(message=f"Schema '{schema_request.schema_name}' created successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}')
def get_schema(schema_name: str, request: Request) -> Result:
    """特定スキーマの詳細を取得"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if schema_name not in manager:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager[schema_name]
        return Result(data=schema)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}')
def delete_schema(schema_name: str, request: Request) -> Result:
    """スキーマを削除"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        manager.delete_schema(schema_name)
        manager.save()

        return Result(message=f"Schema '{schema_name}' deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/reload')
def reload_schemas(request: Request) -> Result:
    """スキーマファイルを再読み込み"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))
        manager.reload()

        return Result(message="Schemas reloaded successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/save')
def save_schemas(request: Request) -> Result:
    """スキーマファイルを保存"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))
        manager.save()

        return Result(message="Schemas saved successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
