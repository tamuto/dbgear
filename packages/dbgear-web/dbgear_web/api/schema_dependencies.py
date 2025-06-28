from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional
from ..shared.helpers import get_project
from dbgear.models.dependencies import TableDependencyAnalyzer
from ..shared.dtos import Result

router = APIRouter()


@router.get('/schemas/{schema_name}/tables/{table_name}/dependencies')
def get_table_dependencies(
    schema_name: str,
    table_name: str,
    request: Request,
    left_level: Optional[int] = Query(3, ge=0, le=3, description="Left side dependency level (0-3)"),
    right_level: Optional[int] = Query(3, ge=0, le=3, description="Right side dependency level (0-3)")
) -> Result:
    """
    Get table dependencies with hierarchical levels.

    Args:
        schema_name: Target schema name
        table_name: Target table name
        left_level: Maximum level for left side (objects referencing target table)
        right_level: Maximum level for right side (objects referenced by target table)

    Returns:
        JSON structure containing hierarchical dependency information
    """
    try:
        proj = get_project(request)
        schema_manager = proj.schemas

        # Initialize dependency analyzer with project folder for data source analysis
        analyzer = TableDependencyAnalyzer(
            schema_manager=schema_manager,
            project_folder=proj.folder
        )

        # Analyze dependencies
        dependencies = analyzer.analyze(
            schema_name=schema_name,
            table_name=table_name,
            left_level=left_level,
            right_level=right_level
        )

        return Result(
            data=dependencies,
            message="Table dependencies retrieved successfully"
        )

    except ValueError as e:
        # Handle business logic errors (schema/table not found, invalid parameters)
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get('/schemas/{schema_name}/tables/{table_name}/dependencies/summary')
def get_table_dependencies_summary(
    schema_name: str,
    table_name: str,
    request: Request
) -> Result:
    """
    Get a summary of table dependencies (counts only).

    Useful for UI components that need to show dependency counts without
    fetching full dependency details.
    """
    try:
        proj = get_project(request)
        schema_manager = proj.schemas

        analyzer = TableDependencyAnalyzer(
            schema_manager=schema_manager,
            project_folder=proj.folder
        )

        # Get level 1 dependencies only for counting
        dependencies = analyzer.analyze(
            schema_name=schema_name,
            table_name=table_name,
            left_level=1,
            right_level=1
        )

        # Count dependencies by type
        left_counts = {}
        right_counts = {}

        if "level_1" in dependencies["left"]:
            for dep in dependencies["left"]["level_1"]:
                dep_type = dep["type"]
                left_counts[dep_type] = left_counts.get(dep_type, 0) + 1

        if "level_1" in dependencies["right"]:
            for dep in dependencies["right"]["level_1"]:
                dep_type = dep["type"]
                right_counts[dep_type] = right_counts.get(dep_type, 0) + 1

        summary = {
            "target_table": dependencies["target_table"],
            "left_summary": {
                "total": sum(left_counts.values()),
                "by_type": left_counts
            },
            "right_summary": {
                "total": sum(right_counts.values()),
                "by_type": right_counts
            }
        }

        return Result(
            data=summary,
            message="Table dependencies summary retrieved successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get('/schemas/{schema_name}/dependencies/graph')
def get_schema_dependency_graph(
    schema_name: str,
    request: Request,
    max_level: Optional[int] = Query(2, ge=1, le=3, description="Maximum dependency level for graph")
) -> Result:
    """
    Get a complete dependency graph for all tables in the schema.

    This endpoint is useful for generating ER diagrams or dependency visualization.
    """
    try:
        proj = get_project(request)
        schema_manager = proj.schemas

        if not schema_manager.schema_exists(schema_name):
            raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

        schema = schema_manager.get_schema(schema_name)
        analyzer = TableDependencyAnalyzer(
            schema_manager=schema_manager,
            project_folder=proj.folder
        )

        # Build graph data structure
        nodes = []
        edges = []

        # Add all tables as nodes
        for table_name in schema.tables:
            nodes.append({
                "id": f"{schema_name}.{table_name}",
                "type": "table",
                "schema_name": schema_name,
                "table_name": table_name,
                "label": table_name
            })

        # Add all views as nodes
        for view_name in schema.views:
            nodes.append({
                "id": f"{schema_name}.{view_name}",
                "type": "view",
                "schema_name": schema_name,
                "view_name": view_name,
                "label": view_name
            })

        # Analyze dependencies for each table to create edges
        for table_name in schema.tables:
            try:
                deps = analyzer.analyze(
                    schema_name=schema_name,
                    table_name=table_name,
                    left_level=0,  # We only need right side for graph
                    right_level=max_level
                )

                # Create edges from dependencies
                for level_key, level_deps in deps["right"].items():
                    for dep in level_deps:
                        if dep["type"] == "relation" and dep["table_name"]:
                            # Foreign key relationship
                            edges.append({
                                "source": f"{schema_name}.{table_name}",
                                "target": f"{dep['schema_name']}.{dep['table_name']}",
                                "type": "relation",
                                "label": dep["object_name"],
                                "details": dep["details"]
                            })
                        elif dep["type"] == "view":
                            # View dependency (view references table)
                            edges.append({
                                "source": f"{dep['schema_name']}.{dep['object_name']}",
                                "target": f"{schema_name}.{table_name}",
                                "type": "view_reference",
                                "label": "references"
                            })

            except Exception:
                # Skip tables that can't be analyzed
                continue

        graph = {
            "nodes": nodes,
            "edges": edges,
            "schema_name": schema_name,
            "max_level": max_level
        }

        return Result(
            data=graph,
            message="Schema dependency graph retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
