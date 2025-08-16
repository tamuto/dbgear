import argparse
from uuid import uuid4

import uvicorn
from fasthtml.common import *  # noqa
from monsterui.all import *  # noqa

from .layout import layout, content_header, empty_state, breadcrumb
from .project import load_project, get_current_project
from starlette.requests import Request

app, rt = fast_app(hdrs=Theme.blue.headers(highlightjs=True), secret_key=str(uuid4()))


@rt('/')
def index(request: Request):
    """Dashboard page showing project overview."""
    project = get_current_project()

    if not project or not project.is_loaded():
        content = Div(
            content_header(
                "DBGear Editor",
                "No project loaded. Please start the application with --project argument."
            ),
            empty_state(
                "folder-open",
                "No Project Loaded",
                "Use 'dbgear-editor --project /path/to/project' to load a project."
            )
        )
    else:
        project_info = project.get_project_info()
        schemas = project.get_schemas()

        content = Div(
            content_header(
                f"Project: {project_info.get('name', 'Unknown')}",
                f"Located at: {project_info.get('path', 'Unknown')}"
            ),

            # Project statistics
            Div(
                Div(
                    Div(
                        UkIcon("database", height=24, cls="text-blue-500"),
                        Div(
                            H3(str(project_info.get('schemas_count', 0)), cls="text-2xl font-bold text-gray-900"),
                            P("Schemas", cls="text-sm text-gray-500"),
                            cls="ml-3"
                        ),
                        cls="flex items-center"
                    ),
                    cls="bg-white overflow-hidden shadow rounded-lg p-5"
                ),

                Div(
                    Div(
                        UkIcon("table", height=24, cls="text-green-500"),
                        Div(
                            H3(str(project_info.get('tables_count', 0)), cls="text-2xl font-bold text-gray-900"),
                            P("Tables", cls="text-sm text-gray-500"),
                            cls="ml-3"
                        ),
                        cls="flex items-center"
                    ),
                    cls="bg-white overflow-hidden shadow rounded-lg p-5"
                ),

                Div(
                    Div(
                        UkIcon("eye", height=24, cls="text-purple-500"),
                        Div(
                            H3(str(project_info.get('views_count', 0)), cls="text-2xl font-bold text-gray-900"),
                            P("Views", cls="text-sm text-gray-500"),
                            cls="ml-3"
                        ),
                        cls="flex items-center"
                    ),
                    cls="bg-white overflow-hidden shadow rounded-lg p-5"
                ),

                cls="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8"
            ),

            # Recent schemas section
            Div(
                H2("Schemas", cls="text-lg font-medium text-gray-900 mb-4"),
                schema_grid(schemas) if schemas else empty_state(
                    "database",
                    "No Schemas Found",
                    "This project doesn't contain any database schemas yet."
                ),
                cls="bg-white shadow rounded-lg p-6"
            )
        )

    return layout(content, current_path=str(request.url.path))


def schema_grid(schemas: dict):
    """Create a grid of schema cards."""
    if not schemas:
        return Div()

    schema_cards = []
    for schema_name, schema in schemas.items():
        table_count = len(schema.tables) if hasattr(schema, 'tables') else 0
        view_count = len(schema.views) if hasattr(schema, 'views') else 0

        schema_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("database", height=20, cls="text-blue-500"),
                        H3(schema_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    Div(
                        Span(f"{table_count} tables", cls="text-sm text-gray-500 mr-4"),
                        Span(f"{view_count} views", cls="text-sm text-gray-500"),
                        cls="flex"
                    ),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *schema_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


@rt('/schemas')
def schemas(request: Request):
    """Schemas overview page."""
    project = get_current_project()

    if not project or not project.is_loaded():
        return RedirectResponse(url="/")

    schemas = project.get_schemas()

    content = Div(
        content_header(
            "Database Schemas",
            "Manage your database schemas, tables, and views"
        ),

        schema_grid(schemas) if schemas else empty_state(
            "database",
            "No Schemas Found",
            "This project doesn't contain any database schemas yet."
        )
    )

    return layout(content, "Schemas - DBGear Editor", str(request.url.path))


@rt('/schemas/{schema_name}')
def schema_detail(schema_name: str, request: Request):
    """Schema detail page showing tables and views."""
    project = get_current_project()

    if not project or not project.is_loaded():
        return RedirectResponse(url="/")

    schemas = project.get_schemas()
    schema = schemas.get(schema_name)

    if not schema:
        return NotFoundResponse("Schema not found")

    tables = project.get_tables(schema_name).get(schema_name, {})
    views = project.get_views(schema_name).get(schema_name, {})
    procedures = project.get_procedures(schema_name).get(schema_name, {})
    triggers = project.get_triggers(schema_name).get(schema_name, {})

    content = Div(
        breadcrumb(("Schemas", "/schemas"), schema_name),

        content_header(
            f"Schema: {schema_name}",
            f"{len(tables)} tables, {len(views)} views, {len(procedures)} procedures, {len(triggers)} triggers"
        ),

        # Tables section
        Div(
            H2("Tables", cls="text-lg font-medium text-gray-900 mb-4"),
            table_grid(tables, schema_name) if tables else P("No tables in this schema", cls="text-gray-500"),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Views section
        Div(
            H2("Views", cls="text-lg font-medium text-gray-900 mb-4"),
            view_grid(views, schema_name) if views else P("No views in this schema", cls="text-gray-500"),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Procedures section
        Div(
            H2("Stored Procedures", cls="text-lg font-medium text-gray-900 mb-4"),
            procedure_grid(procedures, schema_name) if procedures else P("No procedures in this schema", cls="text-gray-500"),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Triggers section
        Div(
            H2("Triggers", cls="text-lg font-medium text-gray-900 mb-4"),
            trigger_grid(triggers, schema_name) if triggers else P("No triggers in this schema", cls="text-gray-500"),
            cls="bg-white shadow rounded-lg p-6"
        )
    )

    return layout(content, f"{schema_name} - Schemas - DBGear Editor", str(request.url.path))


def table_grid(tables: dict, schema_name: str):
    """Create a grid of table cards."""
    if not tables:
        return Div()

    table_cards = []
    for table_name, table in tables.items():
        column_count = len(table.columns) if hasattr(table, 'columns') else 0

        table_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("table", height=20, cls="text-green-500"),
                        H3(table_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P(f"{column_count} columns", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/tables/{table_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *table_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def view_grid(views: dict, schema_name: str):
    """Create a grid of view cards."""
    if not views:
        return Div()

    view_cards = []
    for view_name, view in views.items():
        view_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("eye", height=20, cls="text-purple-500"),
                        H3(view_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P("SQL View", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/views/{view_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *view_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def procedure_grid(procedures: dict, schema_name: str):
    """Create a grid of procedure cards."""
    if not procedures:
        return Div()

    procedure_cards = []
    for procedure_name, procedure in procedures.items():
        # Determine if it's a function or procedure
        proc_type = "Function" if getattr(procedure, 'is_function', False) else "Procedure"
        param_count = len(getattr(procedure, 'parameters', []))

        procedure_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("zap", height=20, cls="text-orange-500"),
                        H3(procedure_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P(f"{proc_type} ({param_count} parameters)", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/procedures/{procedure_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *procedure_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def trigger_grid(triggers: dict, schema_name: str):
    """Create a grid of trigger cards."""
    if not triggers:
        return Div()

    trigger_cards = []
    for trigger_name, trigger in triggers.items():
        # Get trigger details
        timing = getattr(trigger, 'timing', '')
        event = getattr(trigger, 'event', '')
        table_name = getattr(trigger, 'table_name', '')

        trigger_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("flash", height=20, cls="text-yellow-500"),
                        H3(trigger_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P(f"{timing} {event} on {table_name}", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/triggers/{trigger_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *trigger_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


@rt('/schemas/{schema_name}/procedures/{procedure_name}')
def procedure_detail(schema_name: str, procedure_name: str, request: Request):
    """Procedure detail page showing SQL definition and parameters."""
    project = get_current_project()

    if not project or not project.is_loaded():
        return RedirectResponse(url="/")

    schemas = project.get_schemas()
    schema = schemas.get(schema_name)

    if not schema:
        return NotFoundResponse("Schema not found")

    procedures = project.get_procedures(schema_name).get(schema_name, {})
    procedure = procedures.get(procedure_name)

    if not procedure:
        return NotFoundResponse("Procedure not found")

    content = Div(
        breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), procedure_name),

        content_header(
            f"{'Function' if procedure.is_function else 'Procedure'}: {procedure_name}",
            f"Schema: {schema_name}"
        ),

        # Procedure information card
        Div(
            H2("Procedure Information", cls="text-lg font-medium text-gray-900 mb-4"),
            procedure_info_section(procedure, schema_name, procedure_name),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Parameters section (if any)
        *([
            Div(
                H2("Parameters", cls="text-lg font-medium text-gray-900 mb-4"),
                procedure_parameters_section(procedure),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            )
        ] if len(procedure.parameters) > 0 else []),

        # SQL Body section
        Div(
            H2("SQL Body", cls="text-lg font-medium text-gray-900 mb-4"),
            procedure_sql_section(procedure),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Notes section (if any)
        *([
            Div(
                H2("Notes", cls="text-lg font-medium text-gray-900 mb-4"),
                view_notes_section(procedure),
                cls="bg-white shadow rounded-lg p-6"
            )
        ] if len(list(procedure.notes)) > 0 else [])
    )

    return layout(content, f"{procedure_name} - {schema_name} - DBGear Editor", str(request.url.path))


def procedure_info_section(procedure, schema_name: str, procedure_name: str):
    """Create procedure information section."""
    info_items = [
        ("Name", procedure_name),
        ("Display Name", procedure.display_name),
        ("Type", "Function" if procedure.is_function else "Stored Procedure"),
        ("Schema", schema_name),
        ("Language", procedure.language),
        ("Security Type", procedure.security_type),
    ]

    if procedure.is_function and procedure.return_type:
        info_items.append(("Return Type", procedure.return_type))

    info_items.extend([
        ("Deterministic", "Yes" if procedure.deterministic else "No"),
        ("Reads SQL Data", "Yes" if procedure.reads_sql_data else "No"),
        ("Modifies SQL Data", "Yes" if procedure.modifies_sql_data else "No"),
    ])

    return Div(
        *[
            Div(
                Div(label, cls="text-sm font-medium text-gray-500"),
                Div(value, cls="text-sm text-gray-900"),
                cls="py-2"
            )
            for label, value in info_items
        ],
        cls="grid grid-cols-1 gap-2 sm:grid-cols-3"
    )


def procedure_parameters_section(procedure):
    """Create procedure parameters section."""
    parameters = procedure.parameters

    if not parameters:
        return P("No parameters defined", cls="text-gray-500")

    return Div(
        Table(
            Thead(
                Tr(
                    Th("Parameter Name", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Type", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Data Type", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Default Value", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                ),
                cls="bg-gray-50"
            ),
            Tbody(
                *[parameter_row(param) for param in parameters],
                cls="bg-white divide-y divide-gray-200"
            ),
            cls="min-w-full table-auto"
        ),
        cls="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg"
    )


def parameter_row(parameter):
    """Create a table row for a parameter."""
    param_type_badge = {
        "IN": "bg-blue-100 text-blue-800",
        "OUT": "bg-green-100 text-green-800",
        "INOUT": "bg-purple-100 text-purple-800",
    }.get(parameter.parameter_type, "bg-gray-100 text-gray-800")

    return Tr(
        Td(
            Code(parameter.parameter_name, cls="text-sm font-mono text-blue-600"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            Span(
                parameter.parameter_type,
                cls=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {param_type_badge}"
            ),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            Code(parameter.data_type, cls="text-sm font-mono text-gray-900"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            Code(parameter.default_value or "", cls="text-sm font-mono text-gray-500") if parameter.default_value else "",
            cls="px-6 py-4 whitespace-nowrap"
        ),
        cls="hover:bg-gray-50"
    )


def procedure_sql_section(procedure):
    """Create procedure SQL section with syntax highlighting."""
    sql_body = procedure.body

    if not sql_body:
        return P("No SQL body available", cls="text-gray-500")

    # Create markdown with SQL code block for syntax highlighting
    markdown_content = f"""```sql
{sql_body}
```"""

    return Div(
        render_md(markdown_content),
        cls="prose prose-sm max-w-none"
    )


@rt('/schemas/{schema_name}/triggers/{trigger_name}')
def trigger_detail(schema_name: str, trigger_name: str, request: Request = None):
    """Trigger detail page showing SQL definition and metadata."""
    project = get_current_project()

    if not project or not project.is_loaded():
        return RedirectResponse(url="/")

    schemas = project.get_schemas()
    schema = schemas.get(schema_name)

    if not schema:
        return NotFoundResponse("Schema not found")

    triggers = project.get_triggers(schema_name).get(schema_name, {})
    trigger = triggers.get(trigger_name)

    if not trigger:
        return NotFoundResponse("Trigger not found")

    content = Div(
        breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), trigger_name),

        content_header(
            f"Trigger: {trigger_name}",
            f"Schema: {schema_name}"
        ),

        # Trigger information card
        Div(
            H2("Trigger Information", cls="text-lg font-medium text-gray-900 mb-4"),
            trigger_info_section(trigger, schema_name, trigger_name),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # SQL Body section
        Div(
            H2("SQL Body", cls="text-lg font-medium text-gray-900 mb-4"),
            trigger_sql_section(trigger),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Notes section (if any)
        *([
            Div(
                H2("Notes", cls="text-lg font-medium text-gray-900 mb-4"),
                view_notes_section(trigger),
                cls="bg-white shadow rounded-lg p-6"
            )
        ] if len(list(trigger.notes)) > 0 else [])
    )

    return layout(content, f"{trigger_name} - {schema_name} - DBGear Editor", str(request.url.path) if request else "")


def trigger_info_section(trigger, schema_name: str, trigger_name: str):
    """Create trigger information section."""
    timing_badge = {
        "BEFORE": "bg-yellow-100 text-yellow-800",
        "AFTER": "bg-blue-100 text-blue-800",
        "INSTEAD OF": "bg-purple-100 text-purple-800",
    }.get(trigger.timing, "bg-gray-100 text-gray-800")

    event_badge = {
        "INSERT": "bg-green-100 text-green-800",
        "UPDATE": "bg-orange-100 text-orange-800",
        "DELETE": "bg-red-100 text-red-800",
    }.get(trigger.event, "bg-gray-100 text-gray-800")

    info_items = [
        ("Trigger Name", trigger_name),
        ("Display Name", trigger.display_name),
        ("Schema", schema_name),
        ("Target Table", trigger.table_name),
    ]

    return Div(
        *[
            Div(
                Div(label, cls="text-sm font-medium text-gray-500"),
                Div(value, cls="text-sm text-gray-900"),
                cls="py-2"
            )
            for label, value in info_items
        ],
        Div(
            Div("Timing", cls="text-sm font-medium text-gray-500"),
            Span(
                trigger.timing,
                cls=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {timing_badge}"
            ),
            cls="py-2"
        ),
        Div(
            Div("Event", cls="text-sm font-medium text-gray-500"),
            Span(
                trigger.event,
                cls=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {event_badge}"
            ),
            cls="py-2"
        ),
        *([
            Div(
                Div("Condition", cls="text-sm font-medium text-gray-500"),
                Code(trigger.condition, cls="text-sm font-mono text-gray-900"),
                cls="py-2"
            )
        ] if trigger.condition else []),
        cls="grid grid-cols-1 gap-2 sm:grid-cols-3"
    )


def trigger_sql_section(trigger):
    """Create trigger SQL section with syntax highlighting."""
    sql_body = trigger.body

    if not sql_body:
        return P("No SQL body available", cls="text-gray-500")

    # Create markdown with SQL code block for syntax highlighting
    markdown_content = f"""```sql
{sql_body}
```"""

    return Div(
        render_md(markdown_content),
        cls="prose prose-sm max-w-none"
    )


@rt('/schemas/{schema_name}/views/{view_name}')
def view_detail(schema_name: str, view_name: str, request: Request = None):
    """View detail page showing SQL definition and metadata."""
    project = get_current_project()

    if not project or not project.is_loaded():
        return RedirectResponse(url="/")

    schemas = project.get_schemas()
    schema = schemas.get(schema_name)

    if not schema:
        return NotFoundResponse("Schema not found")

    views = project.get_views(schema_name).get(schema_name, {})
    view = views.get(view_name)

    if not view:
        return NotFoundResponse("View not found")

    content = Div(
        breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), view_name),

        content_header(
            f"View: {view_name}",
            f"Schema: {schema_name}"
        ),

        # View information card
        Div(
            H2("View Information", cls="text-lg font-medium text-gray-900 mb-4"),
            view_info_section(view, schema_name, view_name),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # SQL Definition section
        Div(
            H2("SQL Definition", cls="text-lg font-medium text-gray-900 mb-4"),
            view_sql_section(view),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Notes section (if any)
        *([
            Div(
                H2("Notes", cls="text-lg font-medium text-gray-900 mb-4"),
                view_notes_section(view),
                cls="bg-white shadow rounded-lg p-6"
            )
        ] if len(list(view.notes)) > 0 else [])
    )

    return layout(content, f"{view_name} - {schema_name} - DBGear Editor", str(request.url.path) if request else "")


def view_info_section(view, schema_name: str, view_name: str):
    """Create view information section."""
    info_items = [
        ("View Name", view_name),
        ("Display Name", getattr(view, 'display_name', view_name)),
        ("Schema", schema_name),
    ]

    # Add view type if available
    if hasattr(view, 'view_type'):
        info_items.append(("View Type", getattr(view, 'view_type', 'Standard')))

    # Add materialized info if available
    if hasattr(view, 'is_materialized'):
        info_items.append(("Materialized", "Yes" if getattr(view, 'is_materialized', False) else "No"))

    return Div(
        *[
            Div(
                Div(label, cls="text-sm font-medium text-gray-500"),
                Div(value, cls="text-sm text-gray-900"),
                cls="py-2"
            )
            for label, value in info_items
        ],
        cls="grid grid-cols-1 gap-2 sm:grid-cols-3"
    )


def view_sql_section(view):
    """Create view SQL section with syntax highlighting."""
    sql_statement = getattr(view, 'sql_statement', None) or getattr(view, 'select_statement', None)

    if not sql_statement:
        return P("No SQL definition available", cls="text-gray-500")

    # Create markdown with SQL code block for syntax highlighting
    markdown_content = f"""```sql
{sql_statement}
```"""

    return Div(
        render_md(markdown_content),
        cls="prose prose-sm max-w-none"
    )


def view_notes_section(view):
    """Create view notes section."""
    notes = list(view.notes)

    if not notes:
        return P("No notes available", cls="text-gray-500")

    return Div(
        *[note_card(note) for note in notes],
        cls="space-y-4"
    )


def note_card(note):
    """Create a note information card."""
    return Div(
        Div(
            H3(getattr(note, 'title', 'Note'), cls="text-lg font-medium text-gray-900 mb-2"),
            Div(
                render_md(getattr(note, 'content', '')),
                cls="prose prose-sm max-w-none text-gray-700"
            ),
            cls="p-4"
        ),
        cls="border border-gray-200 rounded-lg"
    )


@rt('/schemas/{schema_name}/tables/{table_name}')
def table_detail(schema_name: str, table_name: str, request: Request = None):
    """Table detail page showing column definitions and constraints."""
    project = get_current_project()

    if not project or not project.is_loaded():
        return RedirectResponse(url="/")

    schemas = project.get_schemas()
    schema = schemas.get(schema_name)

    if not schema:
        return NotFoundResponse("Schema not found")

    tables = project.get_tables(schema_name).get(schema_name, {})
    table = tables.get(table_name)

    if not table:
        return NotFoundResponse("Table not found")

    content = Div(
        breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), table_name),

        content_header(
            f"Table: {table_name}",
            f"Schema: {schema_name}"
        ),

        # Table information card
        Div(
            H2("Table Information", cls="text-lg font-medium text-gray-900 mb-4"),
            table_info_section(table, schema_name, table_name),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Columns section
        Div(
            H2("Columns", cls="text-lg font-medium text-gray-900 mb-4"),
            table_columns_section(table),
            cls="bg-white shadow rounded-lg p-6 mb-6"
        ),

        # Indexes section (if any)
        *([
            Div(
                H2("Indexes", cls="text-lg font-medium text-gray-900 mb-4"),
                table_indexes_section(table),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            )
        ] if len(list(table.indexes)) > 0 else []),

        # Relations section (if any)
        *([
            Div(
                H2("Relations", cls="text-lg font-medium text-gray-900 mb-4"),
                table_relations_section(table),
                cls="bg-white shadow rounded-lg p-6"
            )
        ] if len(list(table.relations)) > 0 else [])
    )

    return layout(content, f"{table_name} - {schema_name} - DBGear Editor", str(request.url.path) if request else "")


def table_info_section(table, schema_name: str, table_name: str):
    """Create table information section."""
    mysql_options = table.mysql_options

    info_items = [
        ("Table Name", table_name),
        ("Display Name", table.display_name),
        ("Schema", schema_name),
    ]

    if mysql_options:
        info_items.extend([
            ("Engine", mysql_options.engine or "InnoDB"),
            ("Charset", mysql_options.charset or "Default"),
            ("Collation", mysql_options.collation or "Default"),
        ])

        if mysql_options.auto_increment:
            info_items.append(("Auto Increment", str(mysql_options.auto_increment)))

        if mysql_options.row_format:
            info_items.append(("Row Format", mysql_options.row_format))

    return Div(
        *[
            Div(
                Div(label, cls="text-sm font-medium text-gray-500"),
                Div(value, cls="text-sm text-gray-900"),
                cls="py-2"
            )
            for label, value in info_items
        ],
        cls="grid grid-cols-1 gap-2 sm:grid-cols-3"
    )


def table_columns_section(table):
    """Create table columns section with detailed information."""
    columns = list(table.columns)

    if not columns:
        return P("No columns defined", cls="text-gray-500")

    return Div(
        Table(
            Thead(
                Tr(
                    Th("Column Name", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Data Type", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Nullable", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Default", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Auto Inc", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Primary Key", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                    Th("Description", cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"),
                ),
                cls="bg-gray-50"
            ),
            Tbody(
                *[column_row(column) for column in columns],
                cls="bg-white divide-y divide-gray-200"
            ),
            cls="min-w-full table-auto"
        ),
        cls="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg"
    )


def column_row(column):
    """Create a table row for a column."""
    # Format column type
    col_type = column.column_type
    type_display = col_type.base_type if col_type else "Unknown"

    if col_type and col_type.length:
        type_display += f"({col_type.length}"
        if col_type.precision:
            type_display += f",{col_type.precision}"
        type_display += ")"

    # Create badges for boolean values
    nullable_badge = (
        Span("Yes", cls="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800")
        if column.nullable
        else Span("No", cls="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800")
    )

    auto_inc_badge = (
        Span("Yes", cls="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800")
        if column.auto_increment
        else ""
    )

    primary_key_badge = (
        Span("Yes", cls="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800")
        if column.primary_key
        else ""
    )

    return Tr(
        Td(
            Code(column.column_name, cls="text-sm font-mono text-blue-600"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            Code(type_display, cls="text-sm font-mono text-gray-900"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(nullable_badge, cls="px-6 py-4 whitespace-nowrap"),
        Td(
            Code(column.default_value or "", cls="text-sm font-mono text-gray-500") if column.default_value else "",
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(auto_inc_badge, cls="px-6 py-4 whitespace-nowrap"),
        Td(primary_key_badge, cls="px-6 py-4 whitespace-nowrap"),
        Td(
            column.display_name or "",
            cls="px-6 py-4 text-sm text-gray-900"
        ),
        cls="hover:bg-gray-50"
    )


def table_indexes_section(table):
    """Create table indexes section."""
    indexes = list(table.indexes)

    if not indexes:
        return P("No indexes defined", cls="text-gray-500")

    return Div(
        *[index_card(index) for index in indexes],
        cls="space-y-4"
    )


def index_card(index):
    """Create an index information card."""
    index_type_badge = {
        "PRIMARY": "bg-red-100 text-red-800",
        "UNIQUE": "bg-yellow-100 text-yellow-800",
        "INDEX": "bg-blue-100 text-blue-800",
        "FULLTEXT": "bg-green-100 text-green-800",
        "SPATIAL": "bg-purple-100 text-purple-800",
    }.get(index.index_type, "bg-gray-100 text-gray-800")

    return Div(
        Div(
            Div(
                H3(index.index_name, cls="text-lg font-medium text-gray-900"),
                Span(
                    index.index_type,
                    cls=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {index_type_badge}"
                ),
                cls="flex items-center justify-between"
            ),
            Div(
                Span("Columns: ", cls="font-medium text-gray-700"),
                Span(", ".join([col.column_name for col in index.columns]), cls="text-gray-900"),
                cls="mt-2"
            ),
            *([
                Div(
                    Span("Unique: ", cls="font-medium text-gray-700"),
                    Span("Yes" if index.is_unique else "No", cls="text-gray-900"),
                    cls="mt-1"
                )
            ] if hasattr(index, 'is_unique') else []),
            cls="p-4"
        ),
        cls="border border-gray-200 rounded-lg"
    )


def table_relations_section(table):
    """Create table relations section."""
    relations = list(table.relations)

    if not relations:
        return P("No relations defined", cls="text-gray-500")

    return Div(
        *[relation_card(relation) for relation in relations],
        cls="space-y-4"
    )


def relation_card(relation):
    """Create a relation information card."""
    # Use constraint_name from the actual Relation model
    relation_name = getattr(relation, 'constraint_name', None) or "Foreign Key"

    return Div(
        Div(
            H3(relation_name, cls="text-lg font-medium text-gray-900 mb-2"),
            Div(
                Span("Target Table: ", cls="font-medium text-gray-700"),
                Span(f"{relation.target.schema_name}.{relation.target.table_name}", cls="text-gray-900"),
                cls="mb-1"
            ),
            Div(
                Span("Columns: ", cls="font-medium text-gray-700"),
                Span(
                    " → ".join([
                        f"{bind.source_column} → {bind.target_column}"
                        for bind in relation.bind_columns
                    ]),
                    cls="text-gray-900"
                ),
                cls="mb-1"
            ),
            Div(
                Span("Cardinality: ", cls="font-medium text-gray-700"),
                Span(f"{relation.cardinarity_source} : {relation.cardinarity_target}", cls="text-gray-900"),
                cls="mb-1"
            ),
            Div(
                Span("On Delete: ", cls="font-medium text-gray-700"),
                Span(relation.on_delete, cls="text-gray-900"),
                cls="mb-1"
            ),
            Div(
                Span("On Update: ", cls="font-medium text-gray-700"),
                Span(relation.on_update, cls="text-gray-900"),
                cls="mb-1"
            ),
            *([
                Div(
                    Span("Description: ", cls="font-medium text-gray-700"),
                    Span(relation.description, cls="text-gray-900"),
                )
            ] if relation.description else []),
            cls="p-4"
        ),
        cls="border border-gray-200 rounded-lg"
    )


def main():
    """Main entry point for the dbgear-editor command."""
    parser = argparse.ArgumentParser(description='DBGear FastHTML Editor')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--project', required=True, help='Project directory to load (required)')

    args = parser.parse_args()

    # Load project (required)
    success = load_project(args.project)
    if success:
        print(f"✅ Loaded project from: {args.project}")
    else:
        print(f"❌ Failed to load project from: {args.project}")
        print("Please check that the directory contains a valid project.yaml file.")
        exit(1)

    print(f"🚀 Starting DBGear Editor on http://{args.host}:{args.port}")

    uvicorn.run(
        "dbgear_editor.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
