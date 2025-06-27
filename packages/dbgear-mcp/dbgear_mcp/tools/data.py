"""Data operations MCP tools."""

from typing import Any, Dict, List, Optional
import os
from pathlib import Path

from dbgear.cli.operations import apply
from dbgear.dbio.engine import create_engine
from dbgear.dbio.database import is_exist as database_exists, create as create_database, drop as drop_database
from dbgear.dbio.table import is_exist as table_exists
from dbgear.models.exceptions import DBGearError


def register_data_tools(mcp, server):
    """Register data operations tools."""
    
    @mcp.tool()
    def apply_data(
        host: str,
        environment: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 3306,
        apply_all: bool = False,
        drop_mode: bool = False
    ) -> Dict[str, Any]:
        """Apply data to target database.
        
        Args:
            host: Database host
            environment: Environment name
            username: Database username (optional, will use project config)
            password: Database password (optional, will use project config)
            port: Database port (default: 3306)
            apply_all: Apply all data files
            drop_mode: Drop and recreate database
            
        Returns:
            Dict with apply result
        """
        try:
            project = server.get_project()
            
            # Build connection parameters
            conn_params = {
                "host": host,
                "port": port
            }
            
            if username:
                conn_params["username"] = username
            if password:
                conn_params["password"] = password
            
            # Execute apply command
            result = apply(
                project=project,
                env=environment,
                database=None,  # Apply to all databases in environment
                target=None,
                all='drop' if drop_mode else ('all' if apply_all else None),
                deploy='default'  # Use default deployment
            )
            
            return {
                "success": True,
                "message": f"Data applied successfully to {host}/{environment}",
                "environment": environment,
                "host": host,
                "details": result if isinstance(result, dict) else {"message": str(result)}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def check_database_connection(
        host: str,
        username: str,
        password: str,
        database: Optional[str] = None,
        port: int = 3306
    ) -> Dict[str, Any]:
        """Check database connection.
        
        Args:
            host: Database host
            username: Database username
            password: Database password
            database: Database name (optional)
            port: Database port (default: 3306)
            
        Returns:
            Dict with connection test result
        """
        try:
            engine = create_engine(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database
            )
            
            with engine.connect() as conn:
                # Test basic query
                result = conn.execute("SELECT 1 AS test").fetchone()
                if result and result[0] == 1:
                    return {
                        "success": True,
                        "message": f"Successfully connected to {host}:{port}" + (f"/{database}" if database else ""),
                        "host": host,
                        "port": port,
                        "database": database
                    }
                else:
                    return {"success": False, "error": "Connection test failed"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def list_databases(
        host: str,
        username: str,
        password: str,
        port: int = 3306
    ) -> Dict[str, Any]:
        """List all databases on the server.
        
        Args:
            host: Database host
            username: Database username
            password: Database password
            port: Database port (default: 3306)
            
        Returns:
            Dict with database list
        """
        try:
            engine = create_engine(
                host=host,
                port=port,
                user=username,
                password=password
            )
            
            with engine.connect() as conn:
                result = conn.execute("SHOW DATABASES").fetchall()
                databases = [row[0] for row in result]
                
                return {
                    "success": True,
                    "databases": databases,
                    "count": len(databases),
                    "host": host,
                    "port": port
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def create_database_if_not_exists(
        host: str,
        username: str,
        password: str,
        database: str,
        charset: str = "utf8mb4",
        collation: str = "utf8mb4_unicode_ci",
        port: int = 3306
    ) -> Dict[str, Any]:
        """Create database if it doesn't exist.
        
        Args:
            host: Database host
            username: Database username
            password: Database password
            database: Database name to create
            charset: Character set (default: utf8mb4)
            collation: Collation (default: utf8mb4_unicode_ci)
            port: Database port (default: 3306)
            
        Returns:
            Dict with creation result
        """
        try:
            engine = create_engine(
                host=host,
                port=port,
                user=username,
                password=password
            )
            
            with engine.connect() as conn:
                # Check if database exists
                exists = database_exists(conn, database)
                
                if exists:
                    return {
                        "success": True,
                        "message": f"Database '{database}' already exists",
                        "database": database,
                        "created": False
                    }
                else:
                    # Create database
                    create_database(conn, database, charset, collation)
                    return {
                        "success": True,
                        "message": f"Database '{database}' created successfully",
                        "database": database,
                        "created": True,
                        "charset": charset,
                        "collation": collation
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def drop_database_if_exists(
        host: str,
        username: str,
        password: str,
        database: str,
        port: int = 3306
    ) -> Dict[str, Any]:
        """Drop database if it exists.
        
        Args:
            host: Database host
            username: Database username
            password: Database password
            database: Database name to drop
            port: Database port (default: 3306)
            
        Returns:
            Dict with drop result
        """
        try:
            engine = create_engine(
                host=host,
                port=port,
                user=username,
                password=password
            )
            
            with engine.connect() as conn:
                # Check if database exists
                exists = database_exists(conn, database)
                
                if not exists:
                    return {
                        "success": True,
                        "message": f"Database '{database}' does not exist",
                        "database": database,
                        "dropped": False
                    }
                else:
                    # Drop database
                    drop_database(conn, database)
                    return {
                        "success": True,
                        "message": f"Database '{database}' dropped successfully",
                        "database": database,
                        "dropped": True
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def list_tables_in_database(
        host: str,
        username: str,
        password: str,
        database: str,
        port: int = 3306
    ) -> Dict[str, Any]:
        """List all tables in a database.
        
        Args:
            host: Database host
            username: Database username
            password: Database password
            database: Database name
            port: Database port (default: 3306)
            
        Returns:
            Dict with table list
        """
        try:
            engine = create_engine(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database
            )
            
            with engine.connect() as conn:
                result = conn.execute("SHOW TABLES").fetchall()
                tables = [row[0] for row in result]
                
                return {
                    "success": True,
                    "tables": tables,
                    "count": len(tables),
                    "database": database,
                    "host": host,
                    "port": port
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def get_table_sample_data(
        host: str,
        username: str,
        password: str,
        database: str,
        table: str,
        limit: int = 10,
        port: int = 3306
    ) -> Dict[str, Any]:
        """Get sample data from a table.
        
        Args:
            host: Database host
            username: Database username
            password: Database password
            database: Database name
            table: Table name
            limit: Number of rows to return (default: 10)
            port: Database port (default: 3306)
            
        Returns:
            Dict with sample data
        """
        try:
            engine = create_engine(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database
            )
            
            with engine.connect() as conn:
                # Check if table exists first (simplified check)
                result = conn.execute(f"SHOW TABLES LIKE '{table}'").fetchone()
                if not result:
                    raise DBGearError(f"Table '{table}' does not exist in database '{database}'")
                
                # Get sample data
                result = conn.execute(f"SELECT * FROM `{table}` LIMIT {limit}").fetchall()
                data = [dict(row._mapping) for row in result]
                
                return {
                    "success": True,
                    "table": table,
                    "database": database,
                    "data": data,
                    "row_count": len(data),
                    "limit": limit
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}