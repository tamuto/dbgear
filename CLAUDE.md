# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

DBGear is a **local development tool** for database initial data management. It is designed for developers working locally and does not require production-level security features like authentication or SQL injection protection. The tool focuses on developer experience and ease of use for managing database schemas and initial data through a web interface.

## Monorepo Architecture

DBGear is structured as a monorepo with three independent packages:

- **dbgear**: Core library and CLI tools with built-in import functionality (`packages/dbgear/`)
- **dbgear-editor**: FastHTML-based web editor for schema viewing and editing (`packages/dbgear-editor/`)
- **dbgear-mcp**: MCP server for LLM integration (`packages/dbgear-mcp/`)

### Package Structure

```
packages/
├── dbgear/                    # CLI Package (pip install dbgear)
│   ├── dbgear/
│   │   ├── models/           # Data models and project management
│   │   │   ├── base.py       # Base Pydantic model classes
│   │   │   ├── schema.py     # Schema and SchemaManager classes
│   │   │   ├── table.py      # Table and TableManager classes
│   │   │   ├── column.py     # Column and ColumnManager classes
│   │   │   ├── column_type.py # ColumnType system with registry
│   │   │   ├── view.py       # View and ViewManager classes
│   │   │   ├── index.py      # Index and IndexManager classes
│   │   │   ├── relation.py   # Relation and RelationManager classes
│   │   │   ├── notes.py      # Note and NoteManager classes
│   │   │   ├── project.py    # Project configuration loader
│   │   │   ├── datamodel.py  # Data grid layout models (DataModel, DataSource, SettingInfo)
│   │   │   ├── environ.py    # Environment management models (Environ, EnvironManager)
│   │   │   ├── mapping.py    # Mapping management models (Mapping, MappingManager)
│   │   │   ├── tenant.py     # Multi-tenant models (TenantConfig, TenantRegistry, DatabaseInfo)
│   │   │   ├── const.py      # Constants and enums
│   │   │   └── exceptions.py # Unified exception classes
│   │   ├── dbio/             # Database I/O operations
│   │   │   ├── engine.py     # Database engine abstraction
│   │   │   ├── database.py   # Database operations
│   │   │   ├── table.py      # Table operations
│   │   │   ├── view.py       # View operations
│   │   │   └── templates/    # SQL template engine
│   │   ├── cli/              # CLI-specific functionality
│   │   │   └── operations.py # CLI operation commands
│   │   ├── utils/            # Utility modules
│   │   │   └── populate.py   # Auto-population utilities
│   │   └── main.py           # Main CLI entry point
│   └── pyproject.toml        # CLI package configuration
│
├── dbgear-editor/            # Web Editor Package (pip install dbgear-editor)
│   ├── dbgear_editor/
│   │   ├── main.py           # FastHTML application entry point
│   │   ├── project.py        # Project management and loading
│   │   ├── layout.py         # Main layout components
│   │   ├── components/       # Reusable UI components
│   │   │   ├── header.py     # Header component
│   │   │   └── sidebar.py    # Sidebar navigation component
│   │   ├── routes/           # Modular route handlers
│   │   │   ├── dashboard.py  # Dashboard and schema overview routes
│   │   │   ├── tables.py     # Table detail routes
│   │   │   ├── views.py      # View detail routes
│   │   │   ├── procedures.py # Stored procedure routes
│   │   │   └── triggers.py   # Trigger detail routes
│   │   └── ui/               # UI component modules
│   │       ├── common.py     # Common UI utilities and components
│   │       ├── tables.py     # Table-specific UI components
│   │       ├── views.py      # View-specific UI components
│   │       ├── procedures.py # Procedure-specific UI components
│   │       └── triggers.py   # Trigger-specific UI components
│   ├── README.md
│   └── pyproject.toml        # Editor package configuration (depends on dbgear)
│
└── dbgear-mcp/               # MCP Package (pip install dbgear-mcp)
    ├── dbgear_mcp/
    │   ├── server.py         # FastMCP server implementation
    │   ├── main.py           # MCP server entry point
    │   └── tools/            # MCP tool implementations
    │       ├── schema.py     # Schema management tools
    │       ├── table.py      # Table management tools
    │       ├── data.py       # Data operations tools
    │       └── project.py    # Project management tools
    ├── tests/                # unittest-based test suite
    └── pyproject.toml        # MCP package configuration (depends on dbgear)
```

### Key Components

- **Project Management**: `packages/dbgear/dbgear/models/project.py` - Core project configuration loader
- **Schema Management**: `packages/dbgear/dbgear/models/schema.py` - Schema and SchemaManager classes with CRUD operations and YAML persistence
- **Table Management**: `packages/dbgear/dbgear/models/table.py` - Table and TableManager classes with comprehensive MySQL support (MySQLTableOptions)
- **Column Management**: `packages/dbgear/dbgear/models/column.py` - Column and ColumnManager classes with advanced MySQL attributes (AUTO_INCREMENT, generated columns, charset/collation)
- **Column Type System**: `packages/dbgear/dbgear/models/column_type.py` - ColumnType objects with parsing, validation, and MySQL type registry
- **View Management**: `packages/dbgear/dbgear/models/view.py` - View and ViewManager classes with SQL statement support and future SQL parsing preparation
- **Index Management**: `packages/dbgear/dbgear/models/index.py` - Index and IndexManager classes with PostgreSQL features (partial indexes, include columns)
- **Relation Management**: `packages/dbgear/dbgear/models/relation.py` - Relation and RelationManager classes for comprehensive FK constraints and logical relationships
- **Note System**: `packages/dbgear/dbgear/models/notes.py` - Unified Note and NoteManager classes for documentation across all entities
- **Data Models**: `packages/dbgear/dbgear/models/datamodel.py` - DataModel, DataSource, and DataModelManager for web interface data grid layouts
- **Environment Management**: `packages/dbgear/dbgear/models/environ.py` - Environ and EnvironManager for environment-specific configurations
- **Mapping Management**: `packages/dbgear/dbgear/models/mapping.py` - Mapping and MappingManager for deployment configurations
- **Tenant Management**: `packages/dbgear/dbgear/models/tenant.py` - TenantConfig, TenantRegistry, and DatabaseInfo for multi-tenant support
- **Constants**: `packages/dbgear/dbgear/models/const.py` - Layout types, binding types, and UI constants
- **Exception Handling**: `packages/dbgear/dbgear/models/exceptions.py` - Unified exception hierarchy (DBGearError, DBGearEntityExistsError, etc.)
- **Database Operations**: `packages/dbgear/dbgear/cli/operations.py` - Apply/deploy data to target databases
- **SQL Template Engine**: `packages/dbgear/dbgear/dbio/templates/` - Jinja2-based SQL generation system for maintainable and consistent database operations
- **Schema Importers**: `packages/dbgear/dbgear/importers/` - Dynamic schema import system with A5:SQL Mk-2 support
- **Web Editor Interface**: `packages/dbgear-editor/dbgear_editor/` - FastHTML-based web interface for schema viewing and editing
  - **Modular Route System**: Route handlers organized by entity type (tables, views, procedures, triggers)
  - **Reusable UI Components**: Common UI utilities and entity-specific display components
  - **Project Integration**: Direct integration with dbgear core models for schema management

### Data Flow

1. Project definitions loaded from `project.yaml` (see `etc/test/project.yaml` for example)
2. Schema definitions imported via built-in dynamic importer system (`dbgear import` command or programmatic API)
3. Data stored in YAML format for version control
4. Web editor provides direct FastHTML-based interface for schema viewing and navigation
5. Database operations apply data through SQLAlchemy with Jinja2-based SQL template engine
6. Schema modifications managed through built-in model methods with validation and YAML persistence

## Development Commands

### CLI Package Development
```bash
cd packages/dbgear

# Install dependencies
poetry install

# Apply database changes
poetry run python -m dbgear.main apply localhost development --all drop

# Import A5:SQL Mk-2 schema (built-in functionality)  
poetry run python -m dbgear.main import a5sql_mk2 ../../etc/test/dbgear.a5er --output schema.yaml

# Run tests
poetry run python -m unittest discover
```


### Web Editor Development
```bash
cd packages/dbgear-editor

# Install dependencies (includes dbgear as dependency)
poetry install

# Run web editor server
poetry run dbgear-editor --project ../../etc/test --port 8000

# Development with auto-reload
poetry run dbgear-editor --project ../../etc/test --port 8000 --reload
```

### Testing & Linting

Each package uses taskipy for independent test execution:

#### Core Package Testing
```bash
cd packages/dbgear
task test           # Run all tests (32+ tests including schema management)
task test-fast      # Run fast tests only
task lint           # flake8 code checking
task clean          # Clean build artifacts
```

#### Web Editor Testing
```bash
cd packages/dbgear-editor
task lint           # flake8 code checking
task clean          # Clean build artifacts
task serve          # Start development server
```

#### MCP Package Testing
```bash
cd packages/dbgear-mcp
task test           # Run all tests using unittest framework
task test-fast      # Run fast tests only
task lint           # flake8 code checking
task clean          # Clean build artifacts
task serve          # Start MCP server
```


### Installation & Usage

#### CLI Usage
```bash
# Install core package
pip install dbgear

# Import A5:SQL Mk-2 schema (built-in functionality)
dbgear import a5sql_mk2 schema.a5er --output schema.yaml

# Apply database changes
dbgear apply localhost development --all drop
```

#### Web Editor Usage
```bash
pip install dbgear-editor  # Automatically installs dbgear dependency
dbgear-editor --project ./etc/test --port 8000
```

## Development Guidelines

### Code Quality Focus Areas

As a local development tool, prioritize these aspects when making changes:

1. **Developer Experience**
   - Clear error messages for YAML configuration issues
   - Intuitive CLI commands and options
   - Fast startup and reload times

2. **Code Maintainability**
   - Type safety with TypeScript and Pydantic
   - Clear separation of concerns between packages and layers
   - Consistent naming conventions

3. **Extensibility**
   - Plugin architecture for new definition types
   - Modular frontend components
   - Configurable data binding rules

### Design Philosophy

When proposing solutions or architectural changes, follow this design hierarchy:

1. **Simple Solution First**
   - Always propose the simplest solution that meets requirements first
   - Ask: "Can this be solved by organizing files differently?"
   - Ask: "Can existing classes/functions handle this with minor modifications?"
   - Avoid creating new abstractions unless absolutely necessary

2. **Reuse Over Rebuild**
   - Leverage existing models, managers, and utilities before creating new ones
   - If `SchemaManager` works for the base case, try using it for extensions too
   - Look for patterns already established in the codebase

3. **Filesystem and OS Features**
   - Consider directory structure as part of the solution
   - Use file organization to represent logical relationships
   - Example: `envs/development/schema.yaml` vs. complex in-memory merging

4. **Avoid Over-Engineering**
   - Resist the urge to create "enterprise-grade" solutions for simple problems
   - Don't add layers of abstraction for future flexibility unless that flexibility is explicitly required
   - "Perfect is the enemy of good" - working solutions are better than theoretically perfect ones

5. **Practical Implementation**
   - Prioritize solutions that are easy to understand and maintain
   - Choose approaches that minimize code changes and complexity
   - Consider how the solution will be used in practice, not just in theory

**Example**: For environment-specific schemas, prefer `EnvironManager.get_schema(env_name) -> SchemaManager` over creating new wrapper classes with complex merging logic.

### Package Dependencies

- **dbgear-editor** depends on **dbgear** as an external package dependency  
- **dbgear-mcp** depends on **dbgear** as an external package dependency
- All imports in dependent packages use `from dbgear.models.*` and `from dbgear.dbio.*` syntax
- Core functionality is completely independent and reusable with built-in import capabilities
- Editor and MCP interfaces are optional additions that can be installed separately

### Known Limitations

- **Security**: Designed for local use only - no authentication/authorization
- **Scalability**: Not optimized for large datasets or concurrent users
- **Testing**: Limited test coverage, focus on critical path testing
- **Documentation**: Minimal docs, relies on code readability

### Improvement Priorities

When enhancing DBGear, focus on:

1. **Development workflow improvements** (highest priority)
2. **Error handling and user feedback**
3. **Configuration validation and helpful error messages**
4. **Plugin development documentation**
5. **Test coverage for core data flows**

### Working with the Codebase

- **Code First**: Always read existing code before implementing new functionality - use Read, Grep, and Glob tools to understand actual method names, class structures, and patterns
- **Package Independence**: Each package has its own configuration and can be developed/installed independently
- **Import Paths**: Use absolute imports when referencing across packages (`from dbgear.core.*`)
- **Testing**: Test each package independently in its own directory
- **Version Synchronization**: Keep version numbers synchronized between packages
- **Python**: Use `task lint` before committing Python changes
- **Web Editor Development**: Use `dbgear-editor --reload` for development with auto-reload
- Test configuration changes with the example project in `etc/test/`
- Maintain backward compatibility for existing `project.yaml` files

### DBGear Editor Development Guidelines

When working with the dbgear-editor FastHTML-based web interface:

1. **Modular Architecture**: Follow the established modular structure
   ```python
   # Route handlers in routes/ directory
   from ..ui.tables import table_info_section, table_columns_section
   from ..ui.common import notes_section, info_section
   ```

2. **Component Reuse**: Leverage common UI components for consistency
   ```python
   # Use common utilities from ui/common.py
   content = info_section(info_items)
   badges = badge("Primary", "blue")
   table = data_table(headers, rows)
   ```

3. **Route Registration**: Register routes through dedicated functions
   ```python
   # In main.py
   from .routes.tables import register_table_routes
   register_table_routes(rt)
   ```

4. **UI Component Organization**: Separate UI logic from route handling
   ```python
   # Route handlers focus on data preparation and response
   # UI components handle presentation logic
   ```

5. **Error Handling**: Use proper FastHTML response types
   ```python
   if not project or not project.is_loaded():
       return RedirectResponse(url="/")
   if not schema:
       return NotFoundResponse("Schema not found")
   ```

6. **Project Integration**: Always check project state before rendering
   ```python
   project = get_current_project()
   if not project or not project.is_loaded():
       # Handle no project state
   ```

### Schema Management Guidelines

When working with schema management features:

1. **Schema Validation**: Use Pydantic-based model validation for schema changes before persistence
2. **Referential Integrity**: Use schema model methods to ensure foreign key constraints are maintained
3. **Error Handling**: Use unified exception hierarchy (DBGearError base class) for clear error messages
4. **Testing**: Include both positive and negative test cases for CRUD operations across all Manager classes
5. **Persistence**: Use `SchemaManager.save()` method for YAML persistence with auto-population
6. **Format Compatibility**: Support A5:SQL Mk-2 import and native YAML format through dynamic importer system
7. **Model Usage**: Access entities through Manager classes (TableManager, ColumnManager, etc.) for consistent CRUD operations
8. **Type Safety**: Leverage ColumnType objects and type checking functions for robust schema definitions
9. **Documentation Policy**: Notes are for documentation and version control only - they are NOT reflected in generated SQL or database schemas

### Schema Definition Format

The native YAML schema format supports comprehensive database schema definitions:

#### Core Schema Structure
- **Multiple schemas** in a single YAML file with hierarchical organization
- **Auto-population** rules for automatic name assignment based on YAML keys
- **Column type registry** for custom type definitions and reuse
- **Global notes** for schema-level documentation

#### Table Definitions
- **Column attributes**: column_name, display_name, column_type (ColumnType object), nullable, primary_key, default_value, expression, stored, auto_increment, charset, collation
- **MySQL-specific options**: engine (InnoDB/MyISAM), charset, collation, auto_increment start value, row_format, partitioning (RANGE/LIST/HASH/KEY)
- **Index definitions**: comprehensive index support with type specification (BTREE/HASH/FULLTEXT/SPATIAL), unique constraints, PostgreSQL features (partial indexes, include columns)
- **Relation definitions**: physical FK constraints with ON DELETE/UPDATE actions, logical relationships with cardinality, multi-column binding support

#### View Definitions
- **SQL statements** with SELECT statement storage
- **Future SQL parsing** preparation with ViewColumn placeholders
- **Dependency tracking** foundation for table/view references

#### Advanced Features
- **Note system**: unified documentation across all entities (Schema, Table, Column, View, Index, Relation)
- **Environment integration**: support for environment-specific schema variations
- **Type safety**: ColumnType parsing and validation with MySQL type support (VARCHAR, INT, DECIMAL, ENUM/SET, JSON, etc.)
- **Exception handling**: unified error management with specific exception types

### Testing Configuration

Test files are in `tests/` directory. The test project in `etc/test/` provides example configuration:
- `project.yaml` - Main project configuration
- `dbgear.a5er` - Database schema file (A5:SQL Mk-2 format)
- `schema.yaml` - Database schema file (Native YAML format)
- Data files in YAML format for test scenarios

### Schema Management Testing

The schema management functionality includes comprehensive test coverage:
- **Schema Model Tests**: Column/table/view/index operations, data model integrity
- **Definition Parser Tests**: A5:SQL Mk-2 parsing, MySQL introspection, format validation, error handling
- **File I/O Tests**: YAML persistence, loading, and validation

Test files located in:
- `tests/models/test_*.py` - Core model testing
- `tests/definitions/test_*.py` - Definition parser testing

### Unit Testing Philosophy

DBGear follows a **pragmatic, simple testing approach** prioritizing maintainability over exhaustive coverage:

#### Core Testing Principles
1. **Comprehensive over Granular**: Use fewer tests that cover more functionality comprehensively
2. **Functionality-Focused**: Test actual use cases rather than individual method calls
3. **Resilient to Change**: Avoid tests that break with implementation details changes
4. **Essential Coverage Only**: Focus on core functionality (YAML read/write, data integrity)

#### Current Test Structure
The core package uses 3 consolidated test cases in `tests/test_core_yaml.py`:
- `test_comprehensive_yaml_roundtrip`: Main functionality with complex schema data
- `test_error_handling`: Exception handling for invalid inputs  
- `test_edge_cases`: Minimal configurations and boundary conditions

#### Testing Framework Choice
- **Core Package**: Uses unittest for consistency with existing test structure
- **MCP Package**: Uses unittest as specified in requirements for new packages
- **Web Package**: Uses pytest for API testing capabilities
- **Frontend Package**: Uses build tests and TypeScript compilation checks

#### Testing Guidelines
- **Favor Integration Tests**: Test complete workflows (load project → verify data → save → reload → verify)
- **Avoid Micro-Tests**: Don't test individual getters/setters or simple property access
- **Test Real Scenarios**: Use realistic test data that mirrors actual usage
- **Keep Tests Simple**: Each test should be understandable without deep implementation knowledge
- **Minimize Test Maintenance**: Structure tests to survive refactoring and feature additions

#### When to Add New Tests
- New core functionality (new file formats, major feature additions)
- New error conditions that need explicit handling
- Edge cases discovered through actual usage
- Integration points with external systems

#### When NOT to Add Tests
- Internal implementation details
- Simple property access or basic CRUD operations
- Every possible parameter combination
- Functionality already covered by existing comprehensive tests

**Important**: When adding new unit tests, always update the test documentation in `docs/spec_tests.md` to include:
- Test case descriptions and what they validate
- New test categories or modules
- Updated test counts and coverage metrics
- Any new testing patterns or methodologies used

This ensures the testing documentation stays current and serves as a comprehensive guide for ongoing test development and maintenance.

### SQL Template Engine Architecture

DBGear uses a Jinja2-based SQL template engine for all database operations, providing maintainable and consistent SQL generation:

#### Architecture Overview
```
packages/dbgear/dbgear/core/dbio/templates/
├── __init__.py              # Basic module
├── engine.py                # SQLTemplateEngine class with Jinja2 integration
└── mysql/
    └── __init__.py          # MySQL-specific templates (21 templates total)
```

#### Template Categories
- **Database Operations**: CREATE/DROP/CHECK DATABASE (3 templates)
- **Table Operations**: CREATE/DROP/CHECK tables, backup/restore (7 templates)  
- **View Operations**: CREATE/DROP/CHECK views, dependencies (6 templates)
- **Index Operations**: CREATE with advanced MySQL features (1 template)
- **Foreign Key Operations**: ADD/DROP foreign key constraints via ALTER TABLE (3 templates)
- **Data Operations**: INSERT with parameter binding (1 template)

#### Key Features
- **Jinja2 Integration**: Full template rendering with custom filters
- **Parameter Binding**: Secure SQL generation with proper escaping
- **MySQL Optimization**: Support for advanced MySQL features (generated columns, character sets, foreign keys)
- **Template Naming**: Consistent `mysql_*` convention for easy identification
- **Error Handling**: Template validation and rendering error management
- **Documentation Separation**: Notes are for documentation only and are NOT included in generated SQL

#### Custom Filters
- `join_columns`: Joins column names with backticks (`column1`, `column2`)
- `escape_identifier`: Escapes SQL identifiers with backticks
- `escape_string`: Escapes SQL string values with proper quote handling

#### Usage Example
```python
from dbgear.core.dbio.templates.mysql import template_engine

# Generate CREATE TABLE SQL
sql = template_engine.render('mysql_create_table', env='production', table=table_model)

# Generate with parameters
sql = template_engine.render('mysql_check_table_exists')
result = engine.select_one(conn, sql, {'env': 'testdb', 'table_name': 'users'})
```

#### Template Testing
All templates are comprehensively tested in `tests/test_template_engine.py`:
- 12 test cases covering all template categories
- Generated SQL output for manual verification
- Error handling and edge case validation
- Integration with schema model objects

#### Migration from Direct SQL
All dbio modules have been migrated from direct SQL generation to template-based approach:
- ✅ `database.py`: Complete template migration (3 functions)
- ✅ `table.py`: Complete template migration (7 functions)
- ✅ `view.py`: Complete template migration (6 functions)

This provides a solid foundation for future database engine support while maintaining current MySQL functionality.

### JSON Data Support

DBGear includes comprehensive support for JSON data types in MySQL databases:

#### JSON Column Type Support
- **Column Type System**: Full JSON type support in the `ColumnType` registry
- **Schema Definition**: Native JSON column type specification in YAML schema files
- **Data Validation**: Automatic validation of JSON column definitions

#### JSON Data Processing
- **YAML-to-JSON Conversion**: Automatic conversion of YAML dictionary objects to JSON strings during INSERT operations
- **Data File Format**: Support for structured data in `.dat` files using YAML dictionaries
- **CLI Integration**: Complete support for JSON data through the `dbgear apply` command

#### Implementation Details
- **Conversion Function**: `dbgear.dbio.table._col_conv()` handles automatic dict-to-JSON conversion
- **Template Integration**: JSON INSERT support through the SQL template engine
- **Type Safety**: Proper handling of JSON data types in the column type system

#### Usage Examples
```yaml
# Schema definition with JSON column
schemas:
  main:
    tables:
      products:
        columns:
          - column_name: metadata
            column_type:
              column_type: JSON
              base_type: JSON
            nullable: true

# Data file with JSON content
- id: 1
  metadata:
    i18n:
      ja: "日本語名"
      en: "English Name"
    settings:
      featured: true
      tags: ["electronics", "mobile"]
```

This JSON support enables efficient management of structured data such as internationalization content, configuration settings, and metadata within the DBGear ecosystem.

### Schema Import System Architecture

DBGear implements a dynamic schema import system using importlib for extensible format support:

#### Architecture Overview
```
packages/dbgear/dbgear/core/
├── importer.py                  # Generic importer with dynamic loading
└── importers/                   # Importer modules directory
    ├── __init__.py              # Interface documentation
    └── a5sql_mk2.py             # A5:SQL Mk-2 format importer
```

#### Core Design Principles
- **Dynamic Loading**: Uses importlib to load importer modules at runtime
- **Unified Interface**: All importers implement the same `retrieve(folder, filename, mapping, **kwargs)` function
- **Extensible**: New formats can be added by creating new modules in `importers/`
- **CLI Integration**: Available via `dbgear import` command
- **Error Handling**: Comprehensive error handling with clear user feedback

#### Import Function Interface
```python
def retrieve(folder: str, filename: str, mapping: dict, **kwargs) -> SchemaManager:
    '''
    Import schema from the specified file and return a SchemaManager object.
    
    Args:
        folder: Directory path containing the file
        filename: Name of the file to import  
        mapping: Schema mapping dictionary (e.g., {'MAIN': 'main'})
        **kwargs: Additional options
        
    Returns:
        SchemaManager: The imported schema manager object
    '''
```

#### A5:SQL Mk-2 Importer Features
- **Column Type Conversion**: Automatic conversion to `ColumnType` objects using `parse_column_type()`
- **Foreign Key Support**: Parses A5:SQL relationship definitions into foreign key references
- **Index Support**: Converts A5:SQL index definitions to DBGear index objects
- **Comment Preservation**: Imports field comments as `Note` objects
- **Error Resilience**: Graceful handling of parsing errors with fallback strategies

#### CLI Usage Examples
```bash
# Import A5:SQL Mk-2 file
dbgear import a5sql_mk2 schema.a5er

# Custom output file
dbgear import a5sql_mk2 schema.a5er --output production_schema.yaml

# Schema mapping
dbgear import a5sql_mk2 schema.a5er --mapping "MAIN:production,TEST:development"
```

#### Programmatic Usage
```python
from dbgear.importer import import_schema
from dbgear.models.schema import SchemaManager

# Import schema
schema_manager = import_schema('a5sql_mk2', 'path/to', 'schema.a5er', {'MAIN': 'main'})

# Save to YAML
schema_manager.save('schema.yaml')
```

#### Migration from Legacy Definitions
The import system replaces the previous `definitions/` module structure:
- ✅ `definitions/a5sql_mk2.py` → `importers/a5sql_mk2.py` (enhanced with ColumnType support)
- ✅ `definitions/selectable.py` → Removed (not needed for core functionality)
- ✅ `import.py` → Removed (experimental implementation)

This provides a clean, extensible foundation for supporting additional schema formats in the future while maintaining backward compatibility for A5:SQL Mk-2 workflows.

## Current Implementation State

The schema management system has been completely restructured with a modern, type-safe architecture:

### ✅ Completed Architecture Migration
- **Folder Structure Reorganization**: Moved from `core/` subdirectory to direct `dbgear/` package structure
- **Manager Pattern Implementation**: Each entity (Schema, Table, Column, View, Index, Relation) has a dedicated Manager class
- **Pydantic-Based Models**: All models inherit from `BaseSchema` with automatic validation and serialization
- **Field → Column Rename**: Complete migration from "Field" terminology to "Column" throughout the codebase
- **Type-Safe Column System**: Advanced `ColumnType` class with parsing, validation, and registry system
- **Unified CRUD Operations**: Consistent `add()`, `remove()`, `__getitem__`, `__iter__` across all managers

### 🏗️ New Model Architecture

#### Base Architecture
- **BaseSchema**: Pydantic BaseModel with camelCase alias generation and populate_by_name support
- **Manager Classes**: Provide consistent interface for collections (TableManager, ColumnManager, etc.)
- **Type Safety**: Complete TypeScript-like type hints and runtime validation

#### Schema Management (`schema.py`)
- **SchemaManager**: Top-level container with load/save methods and YAML serialization
- **Schema**: Individual schema with table, view, and note collections
- **Auto-population**: Smart key-based population using `utils/populate.py`

#### Table Management (`table.py`)
- **Table**: Complete table definition with MySQL-specific options
- **TableManager**: Dictionary-like interface for table collections
- **MySQLTableOptions**: Dedicated class for engine, charset, partitioning, etc.

#### Column Management (`column.py`)
- **Column**: Rich column definition with expressions, charset, collation support
- **ColumnManager**: Supports both index and name-based access
- **Advanced Features**: AUTO_INCREMENT, stored/virtual columns, default values

#### Column Type System (`column_type.py`)
- **ColumnType**: Structured type definition with base_type, length, precision, scale, items
- **ColumnTypeRegistry**: Type registry with CRUD operations
- **Parsing Functions**: `parse_column_type()` for string-to-object conversion
- **Type Checking**: `is_numeric_type()`, `is_string_type()`, `is_date_time_type()`
- **MySQL Defaults**: Pre-built type definitions for common MySQL types

#### View Management (`view.py`)
- **View**: SQL-based view definition with future SQL parsing support
- **ViewColumn**: Detailed column metadata with source table tracking
- **ViewManager**: Standard collection interface for views

#### Index Management (`index.py`)
- **Index**: Comprehensive index definition with PostgreSQL features
- **IndexManager**: Array-like interface for index collections
- **Advanced Features**: Partial indexes, include columns, storage parameters

#### Relation Management (`relation.py`)
- **Relation**: Foreign key constraints with ON DELETE/UPDATE actions
- **RelationManager**: Collection management for table relationships

#### Note System (`notes.py`)
- **Note**: Title/content notes with checked status for review tracking
- **NoteManager**: Unified note management across all entities
- **Documentation Support**: Schema, table, column, view, index level notes

### 🔄 Integration Status
- **Core Models**: ✅ Complete implementation with comprehensive test coverage
- **File I/O**: ✅ YAML load/save with auto-population and validation
- **CLI Integration**: ✅ Updated to use new model paths (`dbgear.models.*`)
- **Web Editor Interface**: ✅ Complete FastHTML-based modular web interface with route handlers and UI components
- **Database Operations**: ⚠️ Need to update imports from `core.models` to `models`

### 🧪 Testing Architecture
- **Comprehensive Testing**: Single test file `test_core_yaml.py` with 3 test cases
- **Real-world Data**: Complex test data with all MySQL features (partitioning, charset, etc.)
- **Roundtrip Testing**: Full load→modify→save→reload validation
- **Error Handling**: Edge cases and validation error testing

When working with schema functionality, use the new model paths:
- `from dbgear.models.schema import SchemaManager, Schema`
- `from dbgear.models.table import Table, TableManager, MySQLTableOptions`
- `from dbgear.models.column import Column, ColumnManager`
- `from dbgear.models.column_type import ColumnType, ColumnTypeRegistry, parse_column_type, create_simple_column_type`
- `from dbgear.models.view import View, ViewManager, ViewColumn`
- `from dbgear.models.index import Index, IndexManager`
- `from dbgear.models.relation import Relation, RelationManager, EntityInfo, BindColumn`
- `from dbgear.models.notes import Note, NoteManager`
- `from dbgear.models.project import Project`
- `from dbgear.models.environ import Environ, EnvironManager`
- `from dbgear.models.datamodel import DataModel, DataSource, DataModelManager, SettingInfo`
- `from dbgear.models.mapping import Mapping, MappingManager`
- `from dbgear.models.tenant import TenantConfig, TenantRegistry, DatabaseInfo`
- `from dbgear.models.exceptions import DBGearError, DBGearEntityExistsError, DBGearEntityNotFoundError, DBGearEntityRemovalError`

### 🎨 DBGear Editor Architecture

The dbgear-editor package provides a modern, modular web interface built on FastHTML:

#### Modular Design (94% Code Reduction)
- **main.py**: 62 lines (reduced from 1,116 lines)
- **Modular Routes**: Entity-specific route handlers (526 total lines)
- **Reusable UI Components**: Common utilities and entity-specific components (761 total lines)

#### Route Organization
```python
# routes/dashboard.py  - Schema overview and navigation
# routes/tables.py     - Table detail views with columns, indexes, relations
# routes/views.py      - View definitions and SQL display
# routes/procedures.py - Stored procedure parameters and SQL body
# routes/triggers.py   - Trigger timing, events, and SQL body
```

#### UI Component Architecture
```python
# ui/common.py     - Shared utilities (info_section, badge, data_table, sql_section)
# ui/tables.py     - Table-specific components (column rows, index cards, relation cards)
# ui/views.py      - View presentation components
# ui/procedures.py - Procedure parameter tables and badges
# ui/triggers.py   - Trigger info sections with timing/event badges
```

#### Key Features
- **FastHTML Integration**: Server-side rendering with Python-based component generation
- **Direct Model Integration**: No API layer - direct access to dbgear core models
- **Responsive Design**: MonsterUI-based styling with Tailwind CSS classes
- **Syntax Highlighting**: SQL code display with markdown rendering
- **Breadcrumb Navigation**: Hierarchical navigation through schemas and entities

## Future Development

See `ROADMAP.md` for planned feature enhancements including:
- ✅ **Web Interface Modernization** - **COMPLETED**: FastHTML-based dbgear-editor with modular architecture
- Internal schema version management system
- Document generation (ER diagrams, table specifications)
- MCP server integration for LLM operations
- Enhanced database operation commands
- Schema editing capabilities in the web editor

When working on these features, follow the implementation phases and architectural guidelines outlined in the roadmap.