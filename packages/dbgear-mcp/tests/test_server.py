"""Tests for DBGear MCP Server."""

import unittest
import tempfile
import os
from pathlib import Path

from dbgear_mcp.server import DBGearMCPServer
from dbgear.models.schema import SchemaManager, Schema
from dbgear.models.table import Table
from dbgear.models.column import Column
from dbgear.models.column_type import parse_column_type


class TestDBGearMCPServer(unittest.TestCase):
    """Test cases for DBGear MCP Server."""
    
    def test_server_initialization(self):
        """Test server initialization without project."""
        server = DBGearMCPServer()
        self.assertIsNotNone(server.mcp)
        self.assertIsNone(server.project)
        self.assertIsNone(server.current_schema)
    
    def test_schema_operations(self):
        """Test basic schema operations."""
        server = DBGearMCPServer()
        
        # Create test schema
        schema_manager = SchemaManager()
        schema = Schema(name="test_schema")
        
        # Add a test table
        table = Table(instance="test_instance", table_name="users", display_name="Users")
        column = Column(
            column_name="id",
            display_name="ID",
            column_type=parse_column_type("INT"),
            nullable=False,
            primary_key=True
        )
        table.columns.add(column)
        schema.tables.add(table)
        schema_manager.schemas["test_schema"] = schema
        
        # Set schema in server
        server.set_schema(schema_manager)
        
        # Test schema retrieval
        retrieved_schema = server.get_schema()
        self.assertIsNotNone(retrieved_schema)
        self.assertIn("test_schema", retrieved_schema.schemas)
        self.assertIn("users", [t.table_name for t in retrieved_schema.schemas["test_schema"].tables])
    
    def test_schema_file_operations(self):
        """Test schema file save/load operations."""
        server = DBGearMCPServer()
        
        # Create test schema
        schema_manager = SchemaManager()
        schema = Schema(name="file_test")
        table = Table(instance="test_instance", table_name="products", display_name="Products")
        schema.tables.add(table)
        schema_manager.schemas["file_test"] = schema
        
        server.set_schema(schema_manager)
        
        # Test save and load with temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save schema
            schema_manager.save(temp_file)
            self.assertTrue(os.path.exists(temp_file))
            
            # Load schema
            loaded_schema = SchemaManager.load(temp_file)
            self.assertIn("file_test", loaded_schema.schemas)
            self.assertIn("products", [t.table_name for t in loaded_schema.schemas["file_test"].tables])
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()