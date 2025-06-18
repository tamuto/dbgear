from fastapi import APIRouter, Request, HTTPException
from dbgear.core.models.project import project
from dbgear.core.models.schema_manager import SchemaManager
from .dtos import Result, CreateViewRequest, UpdateViewRequest, convert_to_view

router = APIRouter()


@router.get('/schemas/{schema_name}/views')
def get_views(schema_name: str, request: Request) -> Result:
    """スキーマ内のビュー一覧を取得"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager.get_schema(schema_name)
        views = list(schema.views.keys())
        return Result(data=views)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/views')
def create_view(schema_name: str, request: Request, view_request: CreateViewRequest) -> Result:
    """新規ビューを作成"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager.get_schema(schema_name)

        # ビューが既に存在するかチェック
        if view_request.view_name in schema.views:
            raise HTTPException(status_code=400, detail=f"View '{view_request.view_name}' already exists in schema '{schema_name}'")

        view = convert_to_view(view_request)
        schema.add_view(view)
        manager.save()

        return Result(message=f"View '{view_request.view_name}' created successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/views/{view_name}')
def get_view(schema_name: str, view_name: str, request: Request) -> Result:
    """特定ビューの詳細を取得"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager.get_schema(schema_name)

        if view_name not in schema.views:
            raise HTTPException(status_code=404, detail=f"View '{view_name}' not found in schema '{schema_name}'")

        view = schema.views[view_name]
        return Result(data=view)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/views/{view_name}')
def update_view(schema_name: str, view_name: str, request: Request, view_request: UpdateViewRequest) -> Result:
    """ビューを更新"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager.get_schema(schema_name)

        if view_name not in schema.views:
            raise HTTPException(status_code=404, detail=f"View '{view_name}' not found in schema '{schema_name}'")

        existing_view = schema.views[view_name]

        # 既存ビューの値をベースに、リクエストで指定された値のみ更新
        updated_data = existing_view.model_dump()
        request_data = view_request.model_dump(exclude_unset=True)
        updated_data.update(request_data)

        from dbgear.core.models.schema import View
        updated_view = View(**updated_data)

        schema.update_view(view_name, updated_view)
        manager.save()

        return Result(message=f"View '{view_name}' updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/views/{view_name}')
def delete_view(schema_name: str, view_name: str, request: Request) -> Result:
    """ビューを削除"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager.get_schema(schema_name)

        if view_name not in schema.views:
            raise HTTPException(status_code=404, detail=f"View '{view_name}' not found in schema '{schema_name}'")

        schema.delete_view(view_name)
        manager.save()

        return Result(message=f"View '{view_name}' deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
