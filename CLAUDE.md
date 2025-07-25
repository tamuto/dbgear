# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

DBGear is a **local development tool** for database initial data management. It is designed for developers working locally and does not require production-level security features like authentication or SQL injection protection. The tool focuses on developer experience and ease of use for managing database schemas and initial data through a web interface.

## Monorepo Architecture

DBGear is structured as a monorepo with four independent packages:

- **dbgear**: Core library and CLI tools (`packages/dbgear/`)
- **dbgear-import**: Schema and data import functionality (`packages/dbgear-import/`)
- **dbgear-web**: Web interface that depends on dbgear (`packages/dbgear-web/`)
- **frontend**: React frontend package (`packages/frontend/`)

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
├── dbgear-import/            # Import Package (pip install dbgear-import)
│   ├── dbgear_import/
│   │   ├── schema/           # Schema importers
│   │   │   └── a5sql_mk2.py  # A5:SQL Mk-2 importer
│   │   ├── data/             # Data importers (future)
│   │   │   ├── excel.py      # Excel data importer (planned)
│   │   │   └── csv.py        # CSV data importer (planned)
│   │   ├── importer.py       # Generic importer interface
│   │   └── main.py           # Import CLI entry point
│   ├── tests/                # Import functionality tests
│   └── pyproject.toml        # Import package configuration
│
├── dbgear-web/               # Web Package (pip install dbgear-web)
│   ├── dbgear_web/
│   │   ├── api/              # FastAPI routers
│   │   ├── static/           # Frontend build artifacts
│   │   ├── backend.py        # FastAPI application
│   │   └── main.py           # Web server entry point
│   └── pyproject.toml        # Web package configuration (depends on dbgear)
│
├── dbgear-mcp/               # MCP Package (pip install dbgear-mcp)
│   ├── dbgear_mcp/
│   │   ├── server.py         # FastMCP server implementation
│   │   ├── main.py           # MCP server entry point
│   │   └── tools/            # MCP tool implementations
│   │       ├── schema.py     # Schema management tools
│   │       ├── table.py      # Table management tools
│   │       ├── data.py       # Data operations tools
│   │       └── project.py    # Project management tools
│   ├── tests/                # unittest-based test suite
│   └── pyproject.toml        # MCP package configuration (depends on dbgear)
│
├── frontend/                 # New Frontend Package (React/TypeScript + Shadcn/UI)
│   ├── src/
│   │   ├── components/       # Shadcn/UI components
│   │   │   └── ui/          # Generated UI components
│   │   ├── lib/             # Utility functions
│   │   │   └── utils.ts     # Tailwind utility functions
│   │   ├── routes/          # TanStack Router routes
│   │   │   ├── __root.tsx   # Root layout
│   │   │   ├── index.tsx    # Home page
│   │   │   └── about.tsx    # About page
│   │   ├── main.tsx         # Entry point
│   │   ├── routeTree.gen.ts # Generated route tree
│   │   └── globals.css      # Global styles with Tailwind
│   ├── index.html           # HTML template
│   ├── package.json         # Frontend dependencies (pnpm)
│   ├── rsbuild.config.ts    # RSBuild configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── components.json      # Shadcn/UI configuration
│   └── tsconfig.json        # TypeScript configuration
│
└── frontend.bak/            # Previous Frontend (Material-UI based)
    ├── src/
    │   ├── api/              # API hooks and types
    │   ├── components/       # Shared components
    │   ├── features/         # Feature-specific components
    │   ├── resources/        # Assets and i18n
    │   ├── types/           # TypeScript type definitions
    │   ├── main.tsx         # Entry point
    │   └── routes.tsx       # Routing configuration
    ├── public/
    │   └── index.html       # HTML template
    ├── package.json         # Frontend dependencies (pnpm)
    ├── tsconfig.json        # TypeScript configuration
    └── webpack.config.js    # Build configuration
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
- **API Layer**: `packages/dbgear-web/dbgear_web/api/` - FastAPI routers for frontend communication
  - Schema Management APIs: `schemas.py`, `schema_tables.py`, `schema_columns.py`, `schema_indexes.py`, `schema_views.py`, `schema_validation.py`
  - Data Management APIs: `tables.py`, `environs.py`, `project.py`, `refs.py`
- **Frontend Architecture**: New frontend uses Shadcn/UI components with TanStack Router for type-safe routing and RSBuild for fast bundling

### Data Flow

1. Project definitions loaded from `project.yaml` (see `etc/test/project.yaml` for example)
2. Schema definitions imported via dynamic importer system (`dbgear import` command or programmatic API)
3. Data stored in YAML format for version control
4. Frontend communicates with backend via REST API (all endpoints prefixed with `/api`)
5. Database operations apply data through SQLAlchemy with Jinja2-based SQL template engine
6. Schema modifications managed through built-in model methods with validation and YAML persistence

## Development Commands

### CLI Package Development
```bash
cd packages/dbgear

# Install dependencies
poetry install

# Apply database changes (import functionality moved to dbgear-import)
poetry run python -m dbgear.main apply localhost development --all drop

# Run tests
poetry run python -m unittest discover
```

### Import Package Development
```bash
cd packages/dbgear-import

# Install dependencies (includes dbgear as dependency)
poetry install

# Import A5:SQL Mk-2 schema
poetry run dbgear-import schema a5sql_mk2 ../../etc/test/dbgear.a5er --output schema.yaml

# List available importers
poetry run dbgear-import list

# Run tests
poetry run python -m unittest discover
```

### Web Package Development
```bash
cd packages/dbgear-web

# Install dependencies (includes dbgear as dependency)
poetry install

# Run web server
poetry run python -m dbgear_web.main --project ../../etc/test --port 5000
```

### Frontend Development
```bash
cd packages/frontend

# Install dependencies
pnpm install

# Development server (port 8080)
pnpm run dev

# Build for production (outputs to ../dbgear-web/dbgear_web/static/)
pnpm run build
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

#### Web Package Testing
```bash
cd packages/dbgear-web
task test           # Run all tests (14 tests: 11 success, 3 skipped)
task test-fast      # Run fast tests only
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

#### Frontend Testing
```bash
cd packages/frontend

# Build test
pnpm run build
```

### Installation & Usage

#### CLI Usage
```bash
# Install core package
pip install dbgear

# Install import functionality
pip install dbgear-import

# Import A5:SQL Mk-2 schema (now handled by dbgear-import)
dbgear-import schema a5sql_mk2 schema.a5er --output schema.yaml

# Legacy import command (delegates to dbgear-import)
dbgear import a5sql_mk2 schema.a5er --output schema.yaml

# Apply database changes
dbgear apply localhost development --all drop
```

#### Web Interface Usage
```bash
pip install dbgear-web  # Automatically installs dbgear dependency
dbgear-web --project ./etc/test --port 5000
```

### Build Output

- New frontend builds to `packages/dbgear-web/dbgear_web/static/` directory via RSBuild
- Web backend serves static files from this directory at root `/`
- All API endpoints are prefixed with `/api` to avoid conflicts with frontend routes
- TanStack Router handles client-side routing for SPA behavior

### Path Aliases

New frontend uses Shadcn/UI aliases:
- `@/components` → `src/components`
- `@/lib` → `src/lib`
- `@/components/ui` → `src/components/ui`
- `@/hooks` → `src/hooks`

Legacy frontend (frontend.bak) used webpack aliases:
- `~/api/*` → `packages/frontend/src/api/*`
- `~/cmp/*` → `packages/frontend/src/components/*`  
- `~/img/*` → `packages/frontend/src/resources/img/*`

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

- **dbgear-import** depends on **dbgear** as an external package dependency
- **dbgear-web** depends on **dbgear** as an external package dependency  
- **dbgear-mcp** depends on **dbgear** as an external package dependency
- All imports in dependent packages use `from dbgear.models.*` and `from dbgear.dbio.*` syntax
- Core functionality is completely independent and reusable
- Import, web, and MCP interfaces are optional additions that can be installed separately

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
- **Frontend**: Use `pnpm` for package management, new frontend uses RSBuild + TanStack Router + Shadcn/UI
- **Python**: Use `task lint` before committing Python changes
- **Frontend Development**: Use `pnpm run dev` for development server on port 8080
- Test configuration changes with the example project in `etc/test/`
- Maintain backward compatibility for existing `project.yaml` files

### Frontend API Management Guidelines

The new frontend uses a modern API management system that replaces the legacy `nxio.ts` approach:

1. **Use TanStack Query Hooks**: Always use the provided API hooks instead of direct axios calls
   ```typescript
   // ✅ Correct - Use declarative hooks
   const { data, isLoading, error } = useProjects()
   const createProject = useApiPost('/projects')
   
   // ❌ Avoid - Direct API calls
   axios.get('/api/projects').then(...)
   ```

2. **Error Handling**: Leverage the integrated error handling system
   ```typescript
   // Automatic error notifications and retry logic
   const { data } = useProjects({
     onError: (error) => {
       // Custom error handling if needed
       console.error('Failed to load projects:', error)
     }
   })
   ```

3. **Type Safety**: Use proper TypeScript types for all API operations
   ```typescript
   interface Project { id: string; name: string }
   const { data } = useApiQuery<Project[]>(queryKeys.projects(), '/projects')
   ```

4. **Cache Management**: Use invalidation hooks for data consistency
   ```typescript
   const { invalidateProjects } = useInvalidateQueries()
   // Call after mutations to refresh data
   ```

5. **Notifications**: Use the Sonner-based notification system
   ```typescript
   import { notifications } from '@/hooks/use-toast-notifications'
   notifications.success('Operation completed')
   notifications.error('Something went wrong')
   ```

6. **Provider Setup**: Ensure `Providers` component wraps your app root
   ```typescript
   import { Providers } from '@/lib/providers'
   // Wrap your app with <Providers> for TanStack Query and notifications
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
- **Web APIs**: ⚠️ May require updates to match new manager interfaces
- **Frontend**: ⚠️ Field→Column terminology updates needed
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

## Future Development

See `ROADMAP.md` for planned feature enhancements including:
- ✅ UI framework migration (Material-UI → Shadcn/UI) - **COMPLETED**
- ✅ Modern routing system (React Router → TanStack Router) - **COMPLETED**
- ✅ Modern build system (Webpack → RSBuild) - **COMPLETED**
- Internal schema version management system
- Document generation (ER diagrams, table specifications)
- MCP server integration for LLM operations
- Enhanced database operation commands

When working on these features, follow the implementation phases and architectural guidelines outlined in the roadmap.