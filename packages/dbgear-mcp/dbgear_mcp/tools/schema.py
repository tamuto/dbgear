"""Schema management MCP tools."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dbgear.models.schema import SchemaManager, Schema
from dbgear.models.exceptions import DBGearError


def register_schema_tools(mcp, server):
    """Register schema management tools."""
    
    @mcp.tool()
    def load_schema(file_path: str) -> Dict[str, Any]:
        """Load a schema from YAML file.
        
        Args:
            file_path: Path to the schema YAML file
            
        Returns:
            Dict with schema information
        """
        try:
            if not os.path.exists(file_path):
                raise DBGearError(f"Schema file not found: {file_path}")
            
            schema_manager = SchemaManager.load(file_path)
            server.set_schema(schema_manager)
            
            return {
                "success": True,
                "message": f"Schema loaded from {file_path}",
                "schemas": list(schema_manager.schemas.keys()),
                "total_tables": sum(len(schema.tables) for schema in schema_manager.schemas.values()),
                "total_views": sum(len(schema.views) for schema in schema_manager.schemas.values())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def save_schema(file_path: str) -> Dict[str, Any]:
        """Save the current schema to YAML file.
        
        Args:
            file_path: Path to save the schema YAML file
            
        Returns:
            Dict with save result
        """
        try:
            schema_manager = server.get_schema()
            schema_manager.save(file_path)
            
            return {
                "success": True,
                "message": f"Schema saved to {file_path}",
                "schemas": list(schema_manager.schemas.keys())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def list_schemas() -> Dict[str, Any]:
        """List all schemas in the current schema manager.
        
        Returns:
            Dict with schema list and details
        """
        try:
            schema_manager = server.get_schema()
            
            schemas_info = {}
            for schema_name, schema in schema_manager.schemas.items():
                schemas_info[schema_name] = {
                    "tables": list(schema.tables.keys()),
                    "views": list(schema.views.keys()),
                    "table_count": len(schema.tables),
                    "view_count": len(schema.views),
                    "notes": [{"title": note.title, "content": note.content} for note in schema.notes]
                }
            
            return {
                "success": True,
                "schemas": schemas_info,
                "total_schemas": len(schemas_info)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def create_schema(schema_name: str) -> Dict[str, Any]:
        """Create a new schema.
        
        Args:
            schema_name: Name of the new schema
            
        Returns:
            Dict with creation result
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' already exists")
            
            new_schema = Schema(name=schema_name)
            schema_manager.schemas[schema_name] = new_schema
            
            return {
                "success": True,
                "message": f"Schema '{schema_name}' created successfully",
                "schema_name": schema_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def delete_schema(schema_name: str) -> Dict[str, Any]:
        """Delete a schema.
        
        Args:
            schema_name: Name of the schema to delete
            
        Returns:
            Dict with deletion result
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name not in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' not found")
            
            del schema_manager.schemas[schema_name]
            
            return {
                "success": True,
                "message": f"Schema '{schema_name}' deleted successfully",
                "remaining_schemas": list(schema_manager.schemas.keys())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def validate_schema() -> Dict[str, Any]:
        """Validate the current schema for consistency.
        
        Returns:
            Dict with validation results
        """
        try:
            schema_manager = server.get_schema()
            
            validation_results = []
            for schema_name, schema in schema_manager.schemas.items():
                # Basic validation checks
                schema_issues = []
                
                # Check for empty schemas
                if not schema.tables and not schema.views:
                    schema_issues.append("Schema is empty (no tables or views)")
                
                # Check table references in relations
                for table_name, table in schema.tables.items():
                    for relation in table.relations:
                        if relation.referenced_table and relation.referenced_table not in schema.tables:
                            schema_issues.append(f"Table '{table_name}' references non-existent table '{relation.referenced_table}'")
                
                validation_results.append({
                    "schema": schema_name,
                    "valid": len(schema_issues) == 0,
                    "issues": schema_issues
                })
            
            all_valid = all(result["valid"] for result in validation_results)
            
            return {
                "success": True,
                "valid": all_valid,
                "schemas": validation_results,
                "message": "Schema validation completed" + ("" if all_valid else " with issues")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}