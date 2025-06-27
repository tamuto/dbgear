"""DBGear MCP Server using FastMCP."""

import os
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    # For testing without fastmcp
    class FastMCP:
        def __init__(self, name):
            self.name = name

        def tool(self):
            def decorator(func):
                return func
            return decorator

        def run(self):
            pass
from dbgear.models.project import Project
from dbgear.models.schema import SchemaManager
from dbgear.models.exceptions import DBGearError

from .tools.schema import register_schema_tools
from .tools.table import register_table_tools
from .tools.data import register_data_tools
from .tools.project import register_project_tools


class DBGearMCPServer:
    """DBGear MCP Server."""

    def __init__(self, project_path: Optional[str] = None):
        """Initialize the MCP server.

        Args:
            project_path: Path to the DBGear project directory
        """
        self.mcp = FastMCP("DBGear")
        self.project_path = project_path
        self.project: Optional[Project] = None
        self.current_schema: Optional[SchemaManager] = None

        # Register all tools
        self._register_tools()

        # Load project if path provided
        if project_path:
            self._load_project()

    def _register_tools(self):
        """Register all MCP tools."""
        register_schema_tools(self.mcp, self)
        register_table_tools(self.mcp, self)
        register_data_tools(self.mcp, self)
        register_project_tools(self.mcp, self)

    def _load_project(self):
        """Load the DBGear project."""
        try:
            if not os.path.exists(os.path.join(self.project_path, "project.yaml")):
                raise DBGearError(f"No project.yaml found in {self.project_path}")

            self.project = Project.load(self.project_path)
        except Exception as e:
            raise DBGearError(f"Failed to load project: {e}")

    def get_project(self) -> Project:
        """Get the current project."""
        if not self.project:
            raise DBGearError("No project loaded. Use load_project tool first.")
        return self.project

    def get_schema(self) -> SchemaManager:
        """Get the current schema."""
        if not self.current_schema:
            raise DBGearError("No schema loaded. Use load_schema tool first.")
        return self.current_schema

    def set_schema(self, schema: SchemaManager):
        """Set the current schema."""
        self.current_schema = schema

    def run(self):
        """Run the MCP server."""
        return self.mcp.run()
