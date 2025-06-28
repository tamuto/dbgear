from fastapi import APIRouter, Request, HTTPException
from ..shared.helpers import get_project
from dbgear.models.schema import SchemaManager, SchemaValidator
from ..shared.dtos import Result, ValidateTableRequest, ValidateColumnRequest, ValidateForeignKeyRequest

router = APIRouter(prefix='/schemas/validate')


@router.post('/table')
def validate_table(request: Request, validate_request: ValidateTableRequest) -> Result:
    """テーブル構造を検証"""
    try:
        errors = SchemaValidator.validate_table(validate_request.table)

        if errors:
            return Result(
                status='VALIDATION_ERROR',
                message='Table validation failed',
                data={'errors': errors}
            )

        return Result(message='Table validation passed')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/column')
def validate_column(request: Request, validate_request: ValidateColumnRequest) -> Result:
    """カラム定義を検証"""
    try:
        errors = SchemaValidator.validate_column(validate_request.column)

        if errors:
            return Result(
                status='VALIDATION_ERROR',
                message='Column validation failed',
                data={'errors': errors}
            )

        return Result(message='Column validation passed')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/foreign-key')
def validate_foreign_key(request: Request, validate_request: ValidateForeignKeyRequest) -> Result:
    """外部キー参照を検証"""
    try:
        errors = SchemaValidator.validate_foreign_key(validate_request.column, validate_request.schemas)

        if errors:
            return Result(
                status='VALIDATION_ERROR',
                message='Foreign key validation failed',
                data={'errors': errors}
            )

        return Result(message='Foreign key validation passed')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/schema')
def validate_schema(schema_name: str, request: Request) -> Result:
    """スキーマ全体を検証"""
    try:
        proj = get_project(request)
        manager = SchemaManager(proj.definition_file('dbgear_schema'))

        if not manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = manager.get_schema(schema_name)
        all_errors = []

        # 全テーブルを検証
        for table_name, table in schema.tables.items():
            table_errors = SchemaValidator.validate_table(table)
            if table_errors:
                all_errors.extend([f"Table {table_name}: {error}" for error in table_errors])

            # 各カラムを検証
            for column in table.columns:
                column_errors = SchemaValidator.validate_column(column)
                if column_errors:
                    all_errors.extend([f"Table {table_name}, Column {column.column_name}: {error}" for error in column_errors])

                # 外部キー検証
                if column.foreign_key:
                    fk_errors = SchemaValidator.validate_foreign_key(column, {schema_name: schema})
                    if fk_errors:
                        all_errors.extend([f"Table {table_name}, Column {column.column_name} FK: {error}" for error in fk_errors])

        if all_errors:
            return Result(
                status='VALIDATION_ERROR',
                message='Schema validation failed',
                data={'errors': all_errors}
            )

        return Result(message=f"Schema '{schema_name}' validation passed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
