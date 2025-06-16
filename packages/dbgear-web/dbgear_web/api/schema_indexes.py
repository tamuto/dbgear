from fastapi import APIRouter, Request, HTTPException
from dbgear.core.models.project import project
from dbgear.core.models.schema_manager import SchemaManager
from .dtos import Result, CreateIndexRequest, convert_to_index

router = APIRouter(prefix='/schemas/{schema_name}/tables/{table_name}/indexes')


@router.get('')
def get_indexes(schema_name: str, table_name: str, request: Request) -> Result:
    """テーブル内のインデックス一覧を取得"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        indexes = [{"index_name": idx.index_name, "columns": idx.columns} for idx in table.indexes]
        return Result(data=indexes)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('')
def create_index(schema_name: str, table_name: str, request: Request, index_request: CreateIndexRequest) -> Result:
    """新規インデックスを作成"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        # インデックス名が指定されていない場合は自動生成
        if not index_request.index_name:
            index_request.index_name = f"idx_{table_name}_{'_'.join(index_request.columns)}"

        index = convert_to_index(index_request)
        manager.add_index(schema_name, table_name, index)
        manager.save()

        return Result(message=f"Index '{index_request.index_name}' created successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/{index_name}')
def delete_index(schema_name: str, table_name: str, index_name: str, request: Request) -> Result:
    """インデックスを削除"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        # インデックスが存在するかチェック
        index_exists = any(idx.index_name == index_name for idx in table.indexes)
        if not index_exists:
            raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found in table '{table_name}'")

        manager.delete_index(schema_name, table_name, index_name)
        manager.save()

        return Result(message=f"Index '{index_name}' deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
