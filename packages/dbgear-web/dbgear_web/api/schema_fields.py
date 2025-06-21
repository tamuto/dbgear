from fastapi import APIRouter, Request, HTTPException
from dbgear.core.models.project import project
from dbgear.core.models.schema_manager import SchemaManager
from .dtos import Result, CreateFieldRequest, UpdateFieldRequest, convert_to_field

router = APIRouter()


@router.get('/schemas/{schema_name}/tables/{table_name}/fields')
def get_fields(schema_name: str, table_name: str, request: Request) -> Result:
    """テーブル内のフィールド一覧を取得"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        fields = [field.column_name for field in table.fields]
        return Result(data=fields)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schemas/{schema_name}/tables/{table_name}/fields')
def create_field(schema_name: str, table_name: str, request: Request, field_request: CreateFieldRequest) -> Result:
    """新規フィールドを追加"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        field = convert_to_field(field_request)
        manager.add_field(schema_name, table_name, field)
        manager.save()

        return Result(message=f"Field '{field_request.column_name}' added successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/schemas/{schema_name}/tables/{table_name}/fields/{field_name}')
def get_field(schema_name: str, table_name: str, field_name: str, request: Request) -> Result:
    """特定フィールドの詳細を取得"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        field = table.get_field(field_name)
        if field is None:
            raise HTTPException(status_code=404, detail=f"Field '{field_name}' not found in table '{table_name}'")

        return Result(data=field)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put('/schemas/{schema_name}/tables/{table_name}/fields/{field_name}')
def update_field(schema_name: str, table_name: str, field_name: str, request: Request, field_request: UpdateFieldRequest) -> Result:
    """フィールドを更新"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        existing_field = table.get_field(field_name)
        if existing_field is None:
            raise HTTPException(status_code=404, detail=f"Field '{field_name}' not found in table '{table_name}'")

        # 既存フィールドの値をベースに、リクエストで指定された値のみ更新
        updated_data = existing_field.model_dump()
        request_data = field_request.model_dump(exclude_unset=True)
        updated_data.update(request_data)

        from dbgear.core.models.schema import Field
        updated_field = Field(**updated_data)

        manager.update_field(schema_name, table_name, field_name, updated_field)
        manager.save()

        return Result(message=f"Field '{field_name}' updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/schemas/{schema_name}/tables/{table_name}/fields/{field_name}')
def delete_field(schema_name: str, table_name: str, field_name: str, request: Request) -> Result:
    """フィールドを削除"""
    try:
        proj = project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        table = manager.get_table(schema_name, table_name)
        if table is None:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found in schema '{schema_name}'")

        existing_field = table.get_field(field_name)
        if existing_field is None:
            raise HTTPException(status_code=404, detail=f"Field '{field_name}' not found in table '{table_name}'")

        manager.delete_field(schema_name, table_name, field_name)
        manager.save()

        return Result(message=f"Field '{field_name}' deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
