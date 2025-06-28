from fastapi import APIRouter, Request, HTTPException
from ..shared.helpers import get_schema_manager
from ..shared.dtos import Result

router = APIRouter(prefix='/schemas/validate')


@router.post('/{schema_name}')
def validate_schema(schema_name: str, request: Request) -> Result:
    """スキーマ全体を検証（シンプル実装）"""
    try:
        schema_manager = get_schema_manager(request)

        if schema_name not in schema_manager.schemas:
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = schema_manager.schemas[schema_name]
        
        # 基本的な存在チェック
        errors = []
        if not schema.tables:
            errors.append("Schema has no tables")

        if errors:
            return Result(
                status='VALIDATION_ERROR',
                message='Schema validation failed',
                data={'errors': errors}
            )

        return Result(message='Schema validation passed')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))