from fastapi import APIRouter, Request, HTTPException
from ..shared.helpers import get_project
from dbgear.models.schema import SchemaManager
from ..shared.dtos import Result, CreateTableRequest, convert_to_table

router = APIRouter()


@router.get('/schemas/{schema_name}/tables')
def get_tables(schema_name: str, request: Request) -> Result:
    """スキーマ内のテーブル一覧を取得"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if schema_name not in manager:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager[schema_name]
        tables = list(schema.tables.keys())
        return Result(data=tables)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/tables')
def create_table(schema_name: str, request: Request, table_request: CreateTableRequest) -> Result:
    """新規テーブルを作成"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = convert_to_table(table_request)
        manager.add_table(schema_name, table)
        manager.save()

        return Result(message=f"Table '{table_request.table_name}' created successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/tables/{table_name}')
def get_table(schema_name: str, table_name: str, request: Request) -> Result:
    """特定テーブルの詳細を取得"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        return Result(data=table)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/tables/{table_name}')
def update_table(schema_name: str, table_name: str, request: Request, table_request: CreateTableRequest) -> Result:
    """テーブルを更新"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        existing_table = manager.get_table(schema_name, table_name)
        if existing_table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        # 既存のカラムとインデックスを保持しつつ、基本情報を更新
        updated_table = convert_to_table(table_request)
        updated_table.columns = existing_table.columns
        updated_table.indexes = existing_table.indexes

        manager.update_table(schema_name, table_name, updated_table)
        manager.save()

        return Result(message=f"Table '{table_name}' updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/tables/{table_name}')
def delete_table(schema_name: str, table_name: str, request: Request) -> Result:
    """テーブルを削除"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        existing_table = manager.get_table(schema_name, table_name)
        if existing_table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        manager.delete_table(schema_name, table_name)
        manager.save()

        return Result(message=f"Table '{table_name}' deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
