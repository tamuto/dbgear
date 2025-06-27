"""Project management MCP tools."""

from typing import Any, Dict, List, Optional
import os
from pathlib import Path

from dbgear.models.project import Project
from dbgear.models.schema import SchemaManager
from dbgear.models.environ import EnvironManager
from dbgear.models.datamodel import DataModelManager
from dbgear.models.mapping import MappingManager
from dbgear.models.exceptions import DBGearError


def register_project_tools(mcp, server):
    """Register project management tools."""
    
    @mcp.tool()
    def load_project(project_path: str) -> Dict[str, Any]:
        """Load a DBGear project from directory.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dict with project information
        """
        try:
            if not os.path.exists(project_path):
                raise DBGearError(f"Project directory not found: {project_path}")
            
            if not os.path.exists(os.path.join(project_path, "project.yaml")):
                raise DBGearError(f"No project.yaml found in {project_path}")
            
            project = Project.load(project_path)
            server.project = project
            server.project_path = project_path
            
            return {
                "success": True,
                "message": f"Project loaded from {project_path}",
                "project_path": project_path,
                "name": project.name,
                "description": project.description,
                "environments": list(project.environs.keys()) if hasattr(project, 'environs') else [],
                "schemas": list(project.schemas.keys()) if hasattr(project, 'schemas') else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def get_project_info() -> Dict[str, Any]:
        """Get current project information.
        
        Returns:
            Dict with detailed project information
        """
        try:
            project = server.get_project()
            
            info = {
                "success": True,
                "project": {
                    "name": project.name,
                    "description": project.description,
                    "project_path": server.project_path
                }
            }
            
            # Add environment information if available
            if hasattr(project, 'environs') and project.environs:
                environs_info = {}
                for env_name, environ in project.environs.items():
                    environs_info[env_name] = {
                        "name": environ.name,
                        "description": environ.description,
                        "database_info": {
                            "host": environ.database_info.host,
                            "port": environ.database_info.port,
                            "database": environ.database_info.database,
                            "username": environ.database_info.username
                        } if environ.database_info else None
                    }
                info["environments"] = environs_info
            
            # Add schema information if available
            if hasattr(project, 'schemas') and project.schemas:
                schemas_info = {}
                for schema_name, schema in project.schemas.items():
                    schemas_info[schema_name] = {
                        "tables": list(schema.tables.keys()),
                        "views": list(schema.views.keys()),
                        "table_count": len(schema.tables),
                        "view_count": len(schema.views)
                    }
                info["schemas"] = schemas_info
            
            return info
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def list_project_files() -> Dict[str, Any]:
        """List all files in the current project directory.
        
        Returns:
            Dict with file listing
        """
        try:
            if not server.project_path:
                raise DBGearError("No project loaded")
            
            project_path = Path(server.project_path)
            
            files_info = {
                "yaml_files": [],
                "data_files": [],
                "config_files": [],
                "other_files": []
            }
            
            for item in project_path.rglob("*"):
                if item.is_file():
                    relative_path = str(item.relative_to(project_path))
                    
                    if item.suffix in [".yaml", ".yml"]:
                        files_info["yaml_files"].append(relative_path)
                    elif item.suffix in [".dat", ".csv", ".json"]:
                        files_info["data_files"].append(relative_path)
                    elif item.name in ["project.yaml", "config.yaml"] or item.suffix == ".conf":
                        files_info["config_files"].append(relative_path)
                    else:
                        files_info["other_files"].append(relative_path)
            
            return {
                "success": True,
                "project_path": server.project_path,
                "files": files_info,
                "total_files": sum(len(files) for files in files_info.values())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def validate_project() -> Dict[str, Any]:
        """Validate the current project configuration.
        
        Returns:
            Dict with validation results
        """
        try:
            project = server.get_project()
            
            validation_results = {
                "project_config": {"valid": True, "issues": []},
                "environments": {"valid": True, "issues": []},
                "schemas": {"valid": True, "issues": []},
                "data_files": {"valid": True, "issues": []}
            }
            
            # Validate project config
            if not project.name:
                validation_results["project_config"]["issues"].append("Project name is missing")
                validation_results["project_config"]["valid"] = False
            
            # Validate environments
            if hasattr(project, 'environs') and project.environs:
                for env_name, environ in project.environs.items():
                    if not environ.database_info:
                        validation_results["environments"]["issues"].append(f"Environment '{env_name}' missing database info")
                        validation_results["environments"]["valid"] = False
                    elif not all([environ.database_info.host, environ.database_info.database]):
                        validation_results["environments"]["issues"].append(f"Environment '{env_name}' incomplete database info")
                        validation_results["environments"]["valid"] = False
            
            # Validate schemas
            if hasattr(project, 'schemas') and project.schemas:
                for schema_name, schema in project.schemas.items():
                    if not schema.tables and not schema.views:
                        validation_results["schemas"]["issues"].append(f"Schema '{schema_name}' is empty")
                        validation_results["schemas"]["valid"] = False
                    
                    # Check table references
                    for table_name, table in schema.tables.items():
                        for relation in table.relations:
                            if relation.referenced_table and relation.referenced_table not in schema.tables:
                                validation_results["schemas"]["issues"].append(
                                    f"Table '{table_name}' references non-existent table '{relation.referenced_table}'"
                                )
                                validation_results["schemas"]["valid"] = False
            
            # Validate data files
            if server.project_path:
                data_path = Path(server.project_path) / "data"
                if data_path.exists():
                    for data_file in data_path.glob("**/*.dat"):
                        if data_file.stat().st_size == 0:
                            validation_results["data_files"]["issues"].append(f"Empty data file: {data_file.name}")
            
            all_valid = all(result["valid"] for result in validation_results.values())
            
            return {
                "success": True,
                "valid": all_valid,
                "validation_results": validation_results,
                "message": "Project validation completed" + ("" if all_valid else " with issues")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def import_schema_file(
        importer_type: str,
        file_path: str,
        schema_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Import schema from external file.
        
        Args:
            importer_type: Type of importer (e.g., "a5sql_mk2")
            file_path: Path to the file to import
            schema_mapping: Schema name mapping (e.g., {"MAIN": "main"})
            
        Returns:
            Dict with import result
        """
        try:
            from dbgear.importer import import_schema
            
            if not os.path.exists(file_path):
                raise DBGearError(f"Import file not found: {file_path}")
            
            folder = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            mapping = schema_mapping or {}
            
            # Import schema
            schema_manager = import_schema(importer_type, folder, filename, mapping)
            server.set_schema(schema_manager)
            
            return {
                "success": True,
                "message": f"Schema imported from {file_path} using {importer_type} importer",
                "importer_type": importer_type,
                "file_path": file_path,
                "schemas": list(schema_manager.schemas.keys()),
                "total_tables": sum(len(schema.tables) for schema in schema_manager.schemas.values()),
                "total_views": sum(len(schema.views) for schema in schema_manager.schemas.values())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}