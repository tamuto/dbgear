# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

DBGear is a **local development tool** for database initial data management. It is designed for developers working locally and does not require production-level security features like authentication or SQL injection protection. The tool focuses on developer experience and ease of use for managing database schemas and initial data through a web interface.

## Architecture Overview

DBGear is a database management tool for initial data management with a web UI. It consists of:

- **Python Backend (FastAPI)**: Main application in `dbgear/` directory with CLI entry point in `main.py`
- **React Frontend**: TypeScript/React application in `frontend/` directory using Material-UI and Emotion
- **Hybrid Build System**: Poetry for Python dependencies, npm/webpack for frontend assets

### Key Components

- **Project Management**: `dbgear/models/project.py` - Core project configuration loader reading `project.yaml`
- **Data Models**: `dbgear/models/` - Schema definitions, data grids, and environment mappings
- **Database Operations**: `dbgear/operations.py` - Apply/deploy data to target databases
- **API Layer**: `dbgear/api/` - FastAPI routers for frontend communication
- **Frontend State**: Uses Zustand for state management and React Router for navigation

### Data Flow

1. Project definitions loaded from `project.yaml` (see `etc/test/project.yaml` for example)
2. Schema definitions imported via pluggable definition types (a5sql_mk2, mysql, selectable)
3. Data stored in YAML format for version control
4. Frontend communicates with backend via REST API
5. Database operations apply data through SQLAlchemy

## Development Commands

### Python Backend
```bash
# Run development server
poetry run dbgear --project ./etc/test serve

# Run tests
npm run test
# or
poetry run python -m unittest discover

# Lint Python code
npm run flake8:src
npm run flake8:test

# Apply database operations (examples)
npm run run:apply:drop    # Drop and recreate
npm run run:apply:delta   # Apply changes only
npm run run:apply:target  # Apply specific table
```

### Frontend
```bash
# Build for development
npm run build

# Watch mode for development
npm run watch

# Type checking
npm run build:tsc

# Lint TypeScript/React
npm run eslint

# Production build
npm run release
```

### Project Structure

- `dbgear/main.py` - CLI entry point with serve/apply commands
- `dbgear/backend.py` - FastAPI application setup
- `dbgear/models/project.py` - Project configuration management
- `frontend/main.tsx` - React application entry point
- `frontend/routes.tsx` - Application routing configuration
- `webpack.config.js` - Frontend build configuration with path aliases

### Testing

Test files are in `tests/` directory. The test project in `etc/test/` provides example configuration:
- `project.yaml` - Main project configuration
- `dbgear.a5er` - Database schema file
- Data files in YAML format for test scenarios

### Build Output

- Frontend builds to `dbgear/web/` directory
- Backend serves static files from this directory at `/static`
- Root route redirects to `/static` for SPA behavior

### Path Aliases

Frontend uses webpack aliases:
- `~/api/*` → `frontend/api/*`
- `~/cmp/*` → `frontend/components/*`  
- `~/img/*` → `frontend/resources/img/*`

TypeScript also configured with these aliases in `tsconfig.json`.

## Development Guidelines

### Code Quality Focus Areas

As a local development tool, prioritize these aspects when making changes:

1. **Developer Experience**
   - Clear error messages for YAML configuration issues
   - Intuitive CLI commands and options
   - Fast startup and reload times

2. **Code Maintainability**
   - Type safety with TypeScript and Pydantic
   - Clear separation of concerns between layers
   - Consistent naming conventions

3. **Extensibility**
   - Plugin architecture for new definition types
   - Modular frontend components
   - Configurable data binding rules

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

- Always run `npm run flake8:src` before committing Python changes
- Use `npm run watch` for frontend development
- Test configuration changes with the example project in `etc/test/`
- Maintain backward compatibility for existing `project.yaml` files

## Future Development

See `ROADMAP.md` for planned feature enhancements including:
- UI framework migration (Material-UI → Shadcn/UI)
- Internal schema version management system
- Document generation (ER diagrams, table specifications)
- MCP server integration for LLM operations
- Enhanced database operation commands

When working on these features, follow the implementation phases and architectural guidelines outlined in the roadmap.