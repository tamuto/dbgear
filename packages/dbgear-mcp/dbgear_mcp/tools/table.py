"""Table management MCP tools."""

from typing import Any, Dict, List, Optional

from dbgear.models.table import Table, MySQLTableOptions
from dbgear.models.column import Column
from dbgear.models.column_type import parse_column_type
from dbgear.models.index import Index
from dbgear.models.relation import Relation, EntityInfo, BindColumn
from dbgear.models.exceptions import DBGearError


def register_table_tools(mcp, server):
    """Register table management tools."""
    
    @mcp.tool()
    def list_tables(schema_name: str) -> Dict[str, Any]:
        """List all tables in a schema.
        
        Args:
            schema_name: Name of the schema
            
        Returns:
            Dict with table list and details
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name not in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' not found")
            
            schema = schema_manager.schemas[schema_name]
            
            tables_info = {}
            for table_name, table in schema.tables.items():
                tables_info[table_name] = {
                    "display_name": table.display_name,
                    "columns": [col.column_name for col in table.columns],
                    "column_count": len(table.columns),
                    "indexes": [idx.index_name for idx in table.indexes],
                    "index_count": len(table.indexes),
                    "relations": len(table.relations),
                    "notes": len(table.notes),
                    "mysql_options": {
                        "engine": table.mysql_table_options.engine if table.mysql_table_options else None,
                        "charset": table.mysql_table_options.charset if table.mysql_table_options else None,
                        "collation": table.mysql_table_options.collation if table.mysql_table_options else None
                    } if table.mysql_table_options else None
                }
            
            return {
                "success": True,
                "schema": schema_name,
                "tables": tables_info,
                "total_tables": len(tables_info)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def get_table_details(schema_name: str, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table.
        
        Args:
            schema_name: Name of the schema
            table_name: Name of the table
            
        Returns:
            Dict with detailed table information
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name not in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' not found")
            
            schema = schema_manager.schemas[schema_name]
            
            if table_name not in schema.tables:
                raise DBGearError(f"Table '{table_name}' not found in schema '{schema_name}'")
            
            table = schema.tables[table_name]
            
            # Column details
            columns_info = []
            for col in table.columns:
                columns_info.append({
                    "column_name": col.column_name,
                    "display_name": col.display_name,
                    "column_type": {
                        "base_type": col.column_type.base_type,
                        "column_type": col.column_type.column_type,
                        "length": col.column_type.length,
                        "precision": col.column_type.precision,
                        "scale": col.column_type.scale,
                        "items": col.column_type.items
                    },
                    "nullable": col.nullable,
                    "primary_key": col.primary_key,
                    "default_value": col.default_value,
                    "auto_increment": col.auto_increment,
                    "expression": col.expression,
                    "stored": col.stored,
                    "charset": col.charset,
                    "collation": col.collation
                })
            
            # Index details
            indexes_info = []
            for idx in table.indexes:
                indexes_info.append({
                    "index_name": idx.index_name,
                    "display_name": idx.display_name,
                    "columns": [col.column_name for col in idx.columns],
                    "unique": idx.unique,
                    "index_type": idx.index_type,
                    "where_condition": idx.where_condition,
                    "include_columns": [col.column_name for col in idx.include_columns] if idx.include_columns else []
                })
            
            # Relation details
            relations_info = []
            for rel in table.relations:
                relations_info.append({
                    "relation_name": rel.relation_name,
                    "display_name": rel.display_name,
                    "referenced_table": rel.referenced_table,
                    "bind_columns": [{"local": bc.local_column, "foreign": bc.foreign_column} for bc in rel.bind_columns],
                    "on_delete": rel.on_delete,
                    "on_update": rel.on_update
                })
            
            return {
                "success": True,
                "schema": schema_name,
                "table": {
                    "table_name": table.table_name,
                    "display_name": table.display_name,
                    "columns": columns_info,
                    "indexes": indexes_info,
                    "relations": relations_info,
                    "mysql_options": {
                        "engine": table.mysql_table_options.engine,
                        "charset": table.mysql_table_options.charset,
                        "collation": table.mysql_table_options.collation,
                        "auto_increment": table.mysql_table_options.auto_increment,
                        "row_format": table.mysql_table_options.row_format
                    } if table.mysql_table_options else None,
                    "notes": [{"title": note.title, "content": note.content} for note in table.notes]
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def create_table(
        schema_name: str,
        table_name: str,
        display_name: Optional[str] = None,
        engine: str = "InnoDB",
        charset: str = "utf8mb4",
        collation: str = "utf8mb4_unicode_ci"
    ) -> Dict[str, Any]:
        """Create a new table.
        
        Args:
            schema_name: Name of the schema
            table_name: Name of the new table
            display_name: Display name for the table
            engine: MySQL engine (default: InnoDB)
            charset: Character set (default: utf8mb4)
            collation: Collation (default: utf8mb4_unicode_ci)
            
        Returns:
            Dict with creation result
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name not in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' not found")
            
            schema = schema_manager.schemas[schema_name]
            
            if table_name in schema.tables:
                raise DBGearError(f"Table '{table_name}' already exists in schema '{schema_name}'")
            
            # Create MySQL options
            mysql_options = MySQLTableOptions(
                engine=engine,
                charset=charset,
                collation=collation
            )
            
            # Create new table
            new_table = Table(
                table_name=table_name,
                display_name=display_name or table_name,
                mysql_table_options=mysql_options
            )
            
            schema.tables[table_name] = new_table
            
            return {
                "success": True,
                "message": f"Table '{table_name}' created successfully in schema '{schema_name}'",
                "table_name": table_name,
                "schema": schema_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def delete_table(schema_name: str, table_name: str) -> Dict[str, Any]:
        """Delete a table.
        
        Args:
            schema_name: Name of the schema
            table_name: Name of the table to delete
            
        Returns:
            Dict with deletion result
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name not in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' not found")
            
            schema = schema_manager.schemas[schema_name]
            
            if table_name not in schema.tables:
                raise DBGearError(f"Table '{table_name}' not found in schema '{schema_name}'")
            
            del schema.tables[table_name]
            
            return {
                "success": True,
                "message": f"Table '{table_name}' deleted successfully from schema '{schema_name}'",
                "remaining_tables": list(schema.tables.keys())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def add_column(
        schema_name: str,
        table_name: str,
        column_name: str,
        column_type: str,
        nullable: bool = True,
        primary_key: bool = False,
        default_value: Optional[str] = None,
        auto_increment: bool = False,
        display_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a column to a table.
        
        Args:
            schema_name: Name of the schema
            table_name: Name of the table
            column_name: Name of the new column
            column_type: Column type (e.g., "VARCHAR(255)", "INT", "DECIMAL(10,2)")
            nullable: Whether the column can be NULL
            primary_key: Whether this is a primary key column
            default_value: Default value for the column
            auto_increment: Whether the column is auto-increment
            display_name: Display name for the column
            
        Returns:
            Dict with addition result
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name not in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' not found")
            
            schema = schema_manager.schemas[schema_name]
            
            if table_name not in schema.tables:
                raise DBGearError(f"Table '{table_name}' not found in schema '{schema_name}'")
            
            table = schema.tables[table_name]
            
            # Check if column already exists
            for col in table.columns:
                if col.column_name == column_name:
                    raise DBGearError(f"Column '{column_name}' already exists in table '{table_name}'")
            
            # Parse column type
            parsed_type = parse_column_type(column_type)
            
            # Create new column
            new_column = Column(
                column_name=column_name,
                display_name=display_name or column_name,
                column_type=parsed_type,
                nullable=nullable,
                primary_key=primary_key,
                default_value=default_value,
                auto_increment=auto_increment
            )
            
            table.columns.append(new_column)
            
            return {
                "success": True,
                "message": f"Column '{column_name}' added to table '{table_name}' in schema '{schema_name}'",
                "column_name": column_name,
                "table_name": table_name,
                "schema": schema_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def remove_column(schema_name: str, table_name: str, column_name: str) -> Dict[str, Any]:
        """Remove a column from a table.
        
        Args:
            schema_name: Name of the schema
            table_name: Name of the table
            column_name: Name of the column to remove
            
        Returns:
            Dict with removal result
        """
        try:
            schema_manager = server.get_schema()
            
            if schema_name not in schema_manager.schemas:
                raise DBGearError(f"Schema '{schema_name}' not found")
            
            schema = schema_manager.schemas[schema_name]
            
            if table_name not in schema.tables:
                raise DBGearError(f"Table '{table_name}' not found in schema '{schema_name}'")
            
            table = schema.tables[table_name]
            
            # Find and remove column
            for i, col in enumerate(table.columns):
                if col.column_name == column_name:
                    table.columns.pop(i)
                    return {
                        "success": True,
                        "message": f"Column '{column_name}' removed from table '{table_name}' in schema '{schema_name}'",
                        "remaining_columns": [c.column_name for c in table.columns]
                    }
            
            raise DBGearError(f"Column '{column_name}' not found in table '{table_name}'")
            
        except Exception as e:
            return {"success": False, "error": str(e)}