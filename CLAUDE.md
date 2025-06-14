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
└── frontend/                 # Frontend Package (React/TypeScript)
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
    ├── webpack.config.js    # Build configuration
    └── .eslintrc.yml        # ESLint configuration
```

### Key Components

- **Project Management**: `packages/dbgear/dbgear/core/models/project.py` - Core project configuration loader
- **Data Models**: `packages/dbgear/dbgear/core/models/` - Schema definitions, data grids, and environment mappings
- **Database Operations**: `packages/dbgear/dbgear/core/operations.py` - Apply/deploy data to target databases
- **API Layer**: `packages/dbgear-web/dbgear_web/api/` - FastAPI routers for frontend communication
- **Frontend State**: Uses Zustand for state management and React Router for navigation

### Data Flow

1. Project definitions loaded from `project.yaml` (see `etc/test/project.yaml` for example)
2. Schema definitions imported via pluggable definition types (a5sql_mk2, mysql, selectable)
3. Data stored in YAML format for version control
4. Frontend communicates with backend via REST API
5. Database operations apply data through SQLAlchemy

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

# Build for development
pnpm run build

# Build for production
pnpm run build:prod

# Watch mode for development
pnpm run watch

# Development server
pnpm run dev

# Type checking
pnpm run type-check

# Lint TypeScript/React
pnpm run lint
```

### Testing & Linting

Each package uses taskipy for independent test execution:

#### Core Package Testing
```bash
cd packages/dbgear
task test           # Run all tests (11 tests)
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

# TypeScript type checking
pnpm run type-check

# ESLint
pnpm run lint

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

- Frontend builds to `packages/dbgear-web/dbgear_web/static/` directory
- Web backend serves static files from this directory at `/static`
- Root route redirects to `/static` for SPA behavior

### Path Aliases

Frontend uses webpack aliases:
- `~/api/*` → `packages/frontend/src/api/*`
- `~/cmp/*` → `packages/frontend/src/components/*`  
- `~/img/*` → `packages/frontend/src/resources/img/*`

TypeScript also configured with these aliases in `packages/frontend/tsconfig.json`.

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
- **Frontend**: Use `pnpm` for package management, run `pnpm run lint` before committing frontend changes
- **Python**: Use `task lint` before committing Python changes
- **Frontend Development**: Use `pnpm run watch` or `pnpm run dev` for development
- Test configuration changes with the example project in `etc/test/`
- Maintain backward compatibility for existing `project.yaml` files

### Testing Configuration

Test files are in `tests/` directory. The test project in `etc/test/` provides example configuration:
- `project.yaml` - Main project configuration
- `dbgear.a5er` - Database schema file
- Data files in YAML format for test scenarios

**Important**: When adding new unit tests, always update the test documentation in `docs/spec_tests.md` to include:
- Test case descriptions and what they validate
- New test categories or modules
- Updated test counts and coverage metrics
- Any new testing patterns or methodologies used

This ensures the testing documentation stays current and serves as a comprehensive guide for ongoing test development and maintenance.

## Future Development

See `ROADMAP.md` for planned feature enhancements including:
- UI framework migration (Material-UI → Shadcn/UI)
- Internal schema version management system
- Document generation (ER diagrams, table specifications)
- MCP server integration for LLM operations
- Enhanced database operation commands

When working on these features, follow the implementation phases and architectural guidelines outlined in the roadmap.