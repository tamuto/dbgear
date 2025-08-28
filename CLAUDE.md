# CLAUDE.md

This file provides advanced development guidance for Claude Code when working with the DBGear codebase. Basic project information, commands, and conventions are managed through Serena MCP memory system.

## Advanced Development Guidelines

### Critical Package Integration Points

**Import Dependencies Between Packages:**
```python
# dbgear-editor depends on dbgear core
from dbgear.models.schema import SchemaManager, Schema
from dbgear.models.table import Table, TableManager
from dbgear.models.project import Project

# dbgear-mcp depends on dbgear core  
from dbgear.models.schema import SchemaManager
from dbgear.dbio.database import create_database, drop_database
```

### Key Components

**Core Models (`packages/dbgear/dbgear/models/`):**
- `schema.py` - SchemaManager with CRUD and YAML persistence
- `table.py` - TableManager with MySQLTableOptions
- `column.py` - ColumnManager with AUTO_INCREMENT, generated columns
- `column_type.py` - ColumnType registry and parsing system
- `project.py` - Project configuration loader

**Database I/O (`packages/dbgear/dbgear/dbio/`):**
- `templates/` - Jinja2-based SQL generation
- `engine.py` - Database abstraction layer

**Web Editor (`packages/dbgear-editor/`):**
- Modular routes in `routes/` (tables, views, procedures, triggers)
- Reusable UI components in `ui/`


### Design Philosophy

**Critical Design Hierarchy for Architectural Changes:**

1. **Simple Solution First** - Organize files differently before creating abstractions
2. **Reuse Over Rebuild** - Extend existing SchemaManager/TableManager before new classes
3. **Filesystem as Solution** - Use directory structure (e.g., `envs/dev/schema.yaml`)
4. **Avoid Over-Engineering** - Working solutions over theoretical perfection

**Example**: Environment schemas → `EnvironManager.get_schema(env_name)` not wrapper classes

### Import Path Standards

**Cross-package imports must use absolute paths:**
```python
# Correct - dbgear-editor importing from core
from dbgear.models.schema import SchemaManager
from dbgear.models.table import Table, TableManager
from dbgear.models.column_type import parse_column_type

# Incorrect - relative imports fail across packages
from ..models.schema import SchemaManager
```

### DBGear Editor (FastHTML) Integration

**Critical FastHTML Patterns:**
```python
# Route registration in main.py
from .routes.tables import register_table_routes
register_table_routes(rt)

# UI component reuse from ui/common.py
content = info_section(info_items)
table = data_table(headers, rows)

# Project state validation (REQUIRED)
project = get_current_project()
if not project or not project.is_loaded():
    return RedirectResponse(url="/")
```

### Schema Management Critical Rules

1. **Manager Pattern**: Always use TableManager/ColumnManager for CRUD operations
2. **Type Safety**: Use `ColumnType.parse()` for type definitions
3. **Persistence**: Call `SchemaManager.save()` for YAML updates
4. **Notes Policy**: Notes are documentation-only, NOT in generated SQL
5. **Exception Handling**: Use `DBGearError` hierarchy for clear error messages

### Test Project Configuration

**Test data location:** `etc/test/`
- `project.yaml` - Main project configuration
- `dbgear.a5er` - A5:SQL Mk-2 format schema
- `schema.yaml` - Native YAML format schema

**Testing Approach:** Pragmatic integration tests in `tests/test_core_yaml.py`
- 3 comprehensive test cases covering full workflows
- Focus on YAML roundtrip and data integrity
- **Update `docs/spec_tests.md` when adding tests**

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

## Implementation Status & Current State

### ✅ Completed Core Architecture
- **Manager Pattern**: Each entity has dedicated Manager class (SchemaManager, TableManager, etc.)
- **Pydantic Models**: Complete migration with BaseSchema inheritance and validation
- **Type-Safe Column System**: ColumnType class with MySQL registry and parsing
- **YAML Persistence**: Auto-population and roundtrip testing validated

### 🔄 Integration Status
- **Core Models**: ✅ Complete (`dbgear.models.*`)
- **CLI Integration**: ✅ Updated import paths
- **Web Editor**: ✅ FastHTML modular architecture (94% code reduction)
- **Database Operations**: ⚠️ Need import path updates from `core.models` to `models`

### Critical Import Paths
```python
# Schema Management
from dbgear.models.schema import SchemaManager, Schema
from dbgear.models.table import Table, TableManager, MySQLTableOptions
from dbgear.models.column_type import ColumnType, parse_column_type
from dbgear.models.exceptions import DBGearError

# Web Editor Integration  
from dbgear.models.project import Project
```

## Recent Development Achievements (2025-01)

### ✅ UI/UX Major Improvements - COMPLETED

**3-Pane Layout System**:
- Implemented comprehensive Notes display system with right sidebar
- Enhanced Dependencies visualization with 3-column layout (Referenced By → Current Table → References)
- Upgraded ER diagrams with Cytoscape.js dagre/concentric layouts

**Critical Bug Fixes**:
- Fixed Primary Key display issue (0-index problem)
- Changed Primary Key display to numerical order (index + 1)
- Corrected dependency arrow directions to match actual relationships

**Visual Enhancements**:
- Improved note card styling with blue theme and better visibility
- Added visual flow indicators with color coding for dependencies
- Enhanced spacing and layout for better readability

**Technical Architecture**:
```python
# New 3-pane layout signature
def layout(content, title="DBGear Editor", current_path="", sidebar_content=None)

# Right sidebar component structure
def [entity]_notes_sidebar(entity) -> FastHTML
```

**Performance Optimizations**:
- Client-side Cytoscape.js layout computation
- Conditional rendering for right sidebar (Notes存在時のみ)
- Optimized spacing parameters for various screen sizes

### Future Development Priorities

See `ROADMAP.md` for detailed planning:
- ✅ **Web Interface Modernization** - COMPLETED
- ✅ **Notes Display System** - COMPLETED  
- ✅ **Dependencies Visualization** - COMPLETED
- ✅ **ER Diagram Enhancements** - COMPLETED
- Schema version management system
- Enhanced MCP server integration  
- Schema editing capabilities
- Real-time collaboration features