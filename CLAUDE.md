# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

DBGear is a **local development tool** for database initial data management. It is designed for developers working locally and does not require production-level security features like authentication or SQL injection protection. The tool focuses on developer experience and ease of use for managing database schemas and initial data through a web interface.

## Monorepo Architecture

DBGear is structured as a monorepo with three independent packages:

- **dbgear**: Core library and CLI tools (`packages/dbgear/`)
- **dbgear-web**: Web interface that depends on dbgear (`packages/dbgear-web/`)
- **frontend**: React frontend package (`packages/frontend/`)

### Package Structure

```
packages/
├── dbgear/                    # CLI Package (pip install dbgear)
│   ├── dbgear/
│   │   ├── core/             # Core functionality
│   │   │   ├── models/       # Data models and project management
│   │   │   ├── dbio/         # Database I/O operations
│   │   │   ├── definitions/  # Schema definition parsers
│   │   │   └── operations.py # Database operation orchestration
│   │   ├── cli/              # CLI-specific functionality
│   │   │   └── main.py       # CLI entry point
│   │   └── main.py           # Main CLI entry point
│   └── pyproject.toml        # CLI package configuration
│
├── dbgear-web/               # Web Package (pip install dbgear-web)
│   ├── dbgear_web/
│   │   ├── api/              # FastAPI routers
│   │   ├── static/           # Frontend build artifacts
│   │   ├── backend.py        # FastAPI application
│   │   └── main.py           # Web server entry point
│   └── pyproject.toml        # Web package configuration (depends on dbgear)
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

- **Project Management**: `packages/dbgear/dbgear/core/models/project.py` - Core project configuration loader
- **Data Models**: `packages/dbgear/dbgear/core/models/` - Schema definitions, data grids, and environment mappings
- **Schema Management**: `packages/dbgear/dbgear/core/models/schema_manager.py` - CRUD operations for schema definitions
- **Schema Validation**: `packages/dbgear/dbgear/core/models/schema_manager.py` - Validation utilities for tables, fields, and foreign keys
- **Database Operations**: `packages/dbgear/dbgear/core/operations.py` - Apply/deploy data to target databases
- **Definition Parsers**: `packages/dbgear/dbgear/core/definitions/` - Support for a5sql_mk2, mysql, selectable, and dbgear_schema formats
- **API Layer**: `packages/dbgear-web/dbgear_web/api/` - FastAPI routers for frontend communication
  - Schema Management APIs: `schemas.py`, `schema_tables.py`, `schema_fields.py`, `schema_indexes.py`, `schema_views.py`, `schema_validation.py`
  - Data Management APIs: `tables.py`, `environs.py`, `project.py`, `refs.py`
- **Frontend Architecture**: New frontend uses Shadcn/UI components with TanStack Router for type-safe routing and RSBuild for fast bundling

### Data Flow

1. Project definitions loaded from `project.yaml` (see `etc/test/project.yaml` for example)
2. Schema definitions imported via pluggable definition types (a5sql_mk2, mysql, selectable, dbgear_schema)
3. Data stored in YAML format for version control
4. Frontend communicates with backend via REST API (all endpoints prefixed with `/api`)
5. Database operations apply data through SQLAlchemy
6. Schema modifications managed through SchemaManager with validation and persistence

## Development Commands

### CLI Package Development
```bash
cd packages/dbgear

# Install dependencies
poetry install

# Run CLI tools
poetry run python -m dbgear.main apply localhost development --all drop

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

#### Frontend Testing
```bash
cd packages/frontend

# Build test
pnpm run build
```

### Installation & Usage

#### CLI Usage
```bash
pip install dbgear
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

### Package Dependencies

- **dbgear-web** depends on **dbgear** as an external package dependency
- All imports in dbgear-web use `from dbgear.core.*` syntax
- Core functionality is completely independent and reusable
- Web interface is an optional addition that can be installed separately

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

1. **Schema Validation**: Always validate schema changes using `SchemaValidator` before persistence
2. **Referential Integrity**: Use `SchemaManager` methods to ensure foreign key constraints are maintained
3. **Error Handling**: Provide clear error messages for validation failures and constraint violations
4. **Testing**: Include both positive and negative test cases for CRUD operations
5. **Persistence**: Use `manager.save()` to persist changes to YAML files
6. **Format Compatibility**: Support both A5:SQL Mk-2 import and native YAML format

### Schema Definition Format

The native `dbgear_schema` format supports:
- **Multiple schemas** in a single YAML file
- **Field attributes**: column_name, display_name, column_type, nullable, primary_key, default_value, foreign_key, comment
- **Index definitions**: index_name, columns list
- **Schema mapping** for environment-specific names
- **Foreign key validation** across tables within the same schema collection

### Testing Configuration

Test files are in `tests/` directory. The test project in `etc/test/` provides example configuration:
- `project.yaml` - Main project configuration
- `dbgear.a5er` - Database schema file (A5:SQL Mk-2 format)
- `schema.yaml` - Database schema file (DBGear native YAML format)
- Data files in YAML format for test scenarios

### Schema Management Testing

The schema management functionality includes comprehensive test coverage:
- **SchemaValidator Tests**: Field validation, table validation, foreign key validation
- **SchemaManager Tests**: CRUD operations, persistence, referential integrity
- **Schema Model Tests**: Table/field/index operations, data model integrity
- **Definition Parser Tests**: YAML parsing, format validation, error handling

Test files located in:
- `tests/models/test_schema_manager.py` - Schema management CRUD operations (18 tests)
- `tests/definitions/test_dbgear_schema.py` - YAML format parsing (7 tests)

**Important**: When adding new unit tests, always update the test documentation in `docs/spec_tests.md` to include:
- Test case descriptions and what they validate
- New test categories or modules
- Updated test counts and coverage metrics
- Any new testing patterns or methodologies used

This ensures the testing documentation stays current and serves as a comprehensive guide for ongoing test development and maintenance.

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