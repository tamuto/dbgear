# DBGear MCP Server

DBGear MCP (Model Context Protocol) Server provides low-level database management tools for AI assistants using the FastMCP framework.

## Overview

This package exposes DBGear's core database management functionality through MCP tools, allowing AI assistants to:

- Load and manage database schemas
- Create and modify tables, columns, indexes
- Apply data to target databases  
- Manage project configurations
- Import schemas from external formats

## Installation

```bash
# Install dbgear core package first
cd packages/dbgear
poetry install

# Install dbgear-mcp package
cd ../dbgear-mcp
poetry install
```

## Usage

### Start MCP Server

```bash
# Install dependencies first
cd packages/dbgear-mcp
poetry install

# Start without project (limited functionality)
poetry run dbgear-mcp

# Start with project path (recommended)
poetry run dbgear-mcp --project /path/to/project

# Example with test project
poetry run dbgear-mcp --project ../../etc/test/

# The server will output:
# [06/27/25 12:20:05] INFO Starting MCP server 'DBGear' with transport 'stdio'
# Server is now ready to accept MCP protocol messages via stdio
```

### Connect from MCP Client

The server uses `stdio` transport, so it can be integrated with any MCP-compatible AI assistant:

```json
{
  "mcpServers": {
    "dbgear": {
      "command": "poetry",
      "args": ["run", "dbgear-mcp", "--project", "/path/to/project"],
      "cwd": "/path/to/dbgear-mcp"
    }
  }
}
```

### Available Tools

#### Schema Management
- `load_schema(file_path)` - Load schema from YAML file
- `save_schema(file_path)` - Save current schema to YAML file
- `list_schemas()` - List all schemas with details
- `create_schema(schema_name)` - Create new schema
- `delete_schema(schema_name)` - Delete schema
- `validate_schema()` - Validate schema consistency

#### Table Management
- `list_tables(schema_name)` - List tables in schema
- `get_table_details(schema_name, table_name)` - Get detailed table info
- `create_table(schema_name, table_name, ...)` - Create new table
- `delete_table(schema_name, table_name)` - Delete table
- `add_column(schema_name, table_name, column_name, column_type, ...)` - Add column
- `remove_column(schema_name, table_name, column_name)` - Remove column

#### Data Operations
- `apply_data(host, environment, ...)` - Apply data to database
- `check_database_connection(host, username, password, ...)` - Test connection
- `list_databases(host, username, password, ...)` - List databases
- `create_database_if_not_exists(host, username, password, database, ...)` - Create database
- `drop_database_if_exists(host, username, password, database, ...)` - Drop database
- `list_tables_in_database(host, username, password, database, ...)` - List tables
- `get_table_sample_data(host, username, password, database, table, ...)` - Get sample data

#### Project Management
- `load_project(project_path)` - Load DBGear project
- `get_project_info()` - Get project information
- `list_project_files()` - List project files
- `validate_project()` - Validate project configuration
- `import_schema_file(importer_type, file_path, schema_mapping)` - Import external schema

## Example Workflows

### Basic Schema Management

```bash
# MCP Server running at stdio transport
# AI Assistant calls these tools through MCP protocol:

load_schema("/path/to/schema.yaml")
list_schemas()
create_table("main", "users", engine="InnoDB", charset="utf8mb4")
add_column("main", "users", "id", "INT AUTO_INCREMENT PRIMARY KEY")
add_column("main", "users", "name", "VARCHAR(255) NOT NULL")
add_column("main", "users", "email", "VARCHAR(255) UNIQUE")
save_schema("/path/to/updated_schema.yaml")
```

### Database Operations

```bash
# AI Assistant calls these tools through MCP protocol:

check_database_connection("localhost", "root", "password", port=3306)
create_database_if_not_exists("localhost", "root", "password", "myapp_db")
apply_data("localhost", "development", username="root", password="password", apply_all=True)
get_table_sample_data("localhost", "root", "password", "myapp_db", "users", limit=5)
```

### Project Workflow

```bash
# AI Assistant calls these tools through MCP protocol:

load_project("/path/to/dbgear/project")
get_project_info()
import_schema_file("a5sql_mk2", "/path/to/schema.a5er", {"MAIN": "production"})
validate_project()
validate_schema()
```

## Architecture

The MCP server is built with:

- **FastMCP**: Modern Python MCP framework
- **DBGear Core**: Direct integration with dbgear package
- **Tool Categories**: Organized into schema, table, data, and project tools
- **Error Handling**: Consistent error responses with detailed messages
- **Type Safety**: Full type hints and Pydantic model validation

## Development

### Testing

```bash
cd packages/dbgear-mcp
poetry run task test
```

### Linting

```bash
poetry run task lint
```

### Development Server

```bash
# Start MCP server for development
poetry run task serve --project ../../etc/test/

# Or directly
poetry run dbgear-mcp --project ../../etc/test/
```

## Design Philosophy

This MCP server provides **low-level tools only**, following the principle that:

- AI assistants handle high-level business logic and workflow orchestration
- DBGear provides reliable, atomic database operations
- Tools are composable and can be combined for complex operations
- Each tool has a single, well-defined responsibility

This approach maintains DBGear's core focus as a database management tool while enabling powerful AI-assisted database operations.