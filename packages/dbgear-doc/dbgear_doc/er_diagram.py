"""
ER diagram generation module using in4viz library.

Provides SVG and draw.io format output for database schema visualization.
"""

import logging
from pathlib import Path

from in4viz import Table as In4vizTable, Column as In4vizColumn, LineType, Cardinality
from in4viz.backends.svg import SVGERDiagram
from in4viz.backends.drawio import DrawioERDiagram
from dbgear.models.schema import SchemaManager
from dbgear.models.table import Table
from dbgear.models.column import Column

from .diagram import DiagramConfig, load_diagram_config


def collect_related_tables(
    all_tables: dict[str, Table],
    start_qkey: str,
    direction: str,
    level: int,
    visited: set[str] | None = None
) -> set[str]:
    """
    Recursively collect related tables across schemas.

    Args:
        all_tables: Dictionary of tables keyed by ``"schema.table"``
        start_qkey: Qualified key (``"schema.table"``) of the starting table
        direction: 'referenced_by' (tables that reference this) or 'references' (tables this references)
        level: How many levels deep to search
        visited: Set of already visited qualified keys

    Returns:
        Set of qualified keys including the start table
    """
    if visited is None:
        visited = set()

    if level < 0 or start_qkey in visited:
        return visited

    visited.add(start_qkey)

    if level == 0:
        return visited

    start_table = all_tables.get(start_qkey)
    if not start_table:
        return visited

    if direction == 'references':
        # Collect tables that this table references (via foreign keys)
        for relation in start_table.relations:
            target_qkey = f"{relation.target.schema_name}.{relation.target.table_name}"
            if target_qkey in all_tables:
                collect_related_tables(
                    all_tables, target_qkey, direction, level - 1, visited
                )

    elif direction == 'referenced_by':
        start_schema, start_table_name = start_qkey.split('.', 1)
        # Collect tables that reference this table
        for qkey, table in all_tables.items():
            if qkey in visited:
                continue
            for relation in table.relations:
                if (relation.target.schema_name == start_schema
                        and relation.target.table_name == start_table_name):
                    collect_related_tables(
                        all_tables, qkey, direction, level - 1, visited
                    )
                    break

    return visited


def dbgear_to_in4viz_column(column: Column) -> In4vizColumn:
    """
    Convert DBGear Column to in4viz Column.

    Args:
        column: DBGear Column object

    Returns:
        in4viz Column object
    """
    # Get column type display string
    col_type = column.column_type
    type_str = col_type.base_type if col_type else "UNKNOWN"

    if col_type and col_type.length:
        type_str += f"({col_type.length}"
        if col_type.precision:
            type_str += f",{col_type.precision}"
        type_str += ")"

    return In4vizColumn(
        name=column.column_name,
        logical_name=column.display_name or column.column_name,
        type=type_str,
        primary_key=(column.primary_key is not None),
        nullable=column.nullable,
        foreign_key=False,  # Will be set when processing relations
        index=False  # Will be set when processing indexes
    )


def dbgear_to_in4viz_table(
    table: Table,
    table_name: str,
    bgcolor: str = '#ffffff',
    use_gradient: bool = False
) -> In4vizTable:
    """
    Convert DBGear Table to in4viz Table.

    Args:
        table: DBGear Table object
        table_name: Name of the table
        bgcolor: Background color for the table in hex format (default: white)
        use_gradient: Whether to use gradient for background (default: False)

    Returns:
        in4viz Table object
    """
    columns = [dbgear_to_in4viz_column(col) for col in table.columns]

    # Mark foreign key columns
    for relation in table.relations:
        for bind in relation.bind_columns:
            for col in columns:
                if col.name == bind.source_column:
                    col.foreign_key = True

    # Mark indexed columns
    for index in table.indexes:
        for index_col in index.columns:
            for col in columns:
                if col.name == index_col:
                    col.index = True

    return In4vizTable(
        name=table_name,
        logical_name=table.display_name or table_name,
        columns=columns,
        bgcolor=bgcolor,
        use_gradient=use_gradient
    )


def _create_diagram(
    backend: str,
    schema_manager: SchemaManager,
    schema_name: str,
    center_tables: list[str] | None = None,
    referenced_by_level: int = 1,
    references_level: int = 1,
    category: str | None = None,
    diagram_config: DiagramConfig | None = None,
    ideal_length_factor: float = 1.6
):
    """
    Create ER diagram with specified backend.

    Args:
        backend: 'svg' or 'drawio'
        schema_manager: SchemaManager instance
        schema_name: Name of the schema
        center_tables: Names of tables to center the diagram on (None or empty for all tables)
        referenced_by_level: How many levels of tables that reference these tables to include
        references_level: How many levels of tables these tables reference to include
        category: Filter tables by category (None for all tables)
        diagram_config: DiagramConfig for background colors (None uses defaults)
        ideal_length_factor: Multiplier for ideal node distance in force-directed layout
            (smaller values produce tighter diagrams, default: 1.6)

    Returns:
        Diagram instance (SVGERDiagram or DrawioERDiagram)

    Raises:
        ValueError: If schema or table not found
    """
    if diagram_config is None:
        diagram_config = DiagramConfig()

    # Validate default schema exists
    schemas = schema_manager.schemas
    if schema_name not in schemas:
        raise ValueError(f"Schema '{schema_name}' not found")

    # Build global table index across all schemas, keyed by "schema.table".
    # Cross-schema relations are resolved against this index.
    all_tables: dict[str, Table] = {}
    for sname, schema in schemas.items():
        for table in schema.tables:
            all_tables[f"{sname}.{table.table_name}"] = table

    # Filter by category if specified
    if category:
        all_tables = {
            qkey: table for qkey, table in all_tables.items()
            if category in table.categories
        }

    def _resolve_qkey(name: str) -> str:
        # Unqualified names are bound to the default schema; qualified names pass through.
        if '.' in name:
            return name
        return f"{schema_name}.{name}"

    # Determine which tables to include
    if center_tables:
        resolved = [_resolve_qkey(name) for name in center_tables]
        missing = [name for name in resolved if name not in all_tables]
        if missing:
            raise ValueError(f"Table(s) not found: {', '.join(missing)}")

        if len(resolved) == 1:
            center = resolved[0]
            tables_to_include: set[str] = {center}
            if referenced_by_level > 0:
                ref_tables = collect_related_tables(
                    all_tables, center, 'referenced_by', referenced_by_level, set()
                )
                tables_to_include.update(ref_tables)
            if references_level > 0:
                fk_tables = collect_related_tables(
                    all_tables, center, 'references', references_level, set()
                )
                tables_to_include.update(fk_tables)
        else:
            if referenced_by_level > 0 or references_level > 0:
                logging.warning(
                    "Multiple center tables specified; "
                    "--referenced-by-level / --references-level are ignored "
                    "and only the given tables are rendered."
                )
            tables_to_include = set(resolved)
    else:
        # Include all tables from the default schema (legacy behavior)
        tables_to_include = {
            qkey for qkey in all_tables if qkey.split('.', 1)[0] == schema_name
        }

    # Use qualified display names only when the diagram spans multiple schemas,
    # so single-schema diagrams keep their previous appearance.
    distinct_schemas = {qkey.split('.', 1)[0] for qkey in tables_to_include}
    use_qualified_names = len(distinct_schemas) > 1

    def _display_id(qkey: str) -> str:
        if use_qualified_names:
            return qkey
        return qkey.split('.', 1)[1]

    # Create ER diagram with appropriate backend
    if backend == 'svg':
        diagram = SVGERDiagram(
            default_line_type=LineType.ORTHOGONAL,
            min_width=1200,
            min_height=800,
            ideal_length_factor=ideal_length_factor
        )
    else:  # drawio
        diagram = DrawioERDiagram(
            default_line_type=LineType.ORTHOGONAL,
            min_width=1200,
            min_height=800,
            ideal_length_factor=ideal_length_factor
        )

    # Add tables to diagram
    for qkey in tables_to_include:
        table = all_tables[qkey]
        style = diagram_config.get_style(table.categories)
        in4viz_table = dbgear_to_in4viz_table(
            table, _display_id(qkey), style.background_color, style.use_gradient
        )
        diagram.add_table(in4viz_table)

    # Add edges (relationships)
    for qkey in tables_to_include:
        table = all_tables[qkey]
        for relation in table.relations:
            target_qkey = f"{relation.target.schema_name}.{relation.target.table_name}"
            if target_qkey in tables_to_include:
                # Convert cardinality from DBGear format to in4viz format
                cardinality = Cardinality(
                    relation.cardinarity_source,
                    relation.cardinarity_target
                )

                diagram.add_edge(
                    _display_id(qkey),
                    _display_id(target_qkey),
                    LineType.ORTHOGONAL,
                    cardinality
                )

    return diagram


def generate_er_diagram_svg(
    schema_manager: SchemaManager,
    schema_name: str,
    center_tables: list[str] | None = None,
    referenced_by_level: int = 1,
    references_level: int = 1,
    category: str | None = None,
    diagram_config: DiagramConfig | None = None,
    ideal_length_factor: float = 1.6
) -> str:
    """
    Generate ER diagram in SVG format.

    Args:
        schema_manager: SchemaManager instance
        schema_name: Name of the schema
        center_tables: Names of tables to center the diagram on (None or empty for all tables)
        referenced_by_level: How many levels of tables that reference these tables to include
        references_level: How many levels of tables these tables reference to include
        category: Filter tables by category (None for all tables)
        diagram_config: DiagramConfig for background colors (None uses defaults)
        ideal_length_factor: Multiplier for ideal node distance (default: 1.6)

    Returns:
        SVG string of the ER diagram
    """
    diagram = _create_diagram(
        'svg', schema_manager, schema_name, center_tables, referenced_by_level, references_level,
        category, diagram_config, ideal_length_factor
    )
    return diagram.render_svg()


def generate_er_diagram_drawio(
    schema_manager: SchemaManager,
    schema_name: str,
    center_tables: list[str] | None = None,
    referenced_by_level: int = 1,
    references_level: int = 1,
    category: str | None = None,
    diagram_config: DiagramConfig | None = None,
    ideal_length_factor: float = 1.6
) -> str:
    """
    Generate ER diagram in draw.io XML format.

    Args:
        schema_manager: SchemaManager instance
        schema_name: Name of the schema
        center_tables: Names of tables to center the diagram on (None or empty for all tables)
        referenced_by_level: How many levels of tables that reference these tables to include
        references_level: How many levels of tables these tables reference to include
        category: Filter tables by category (None for all tables)
        diagram_config: DiagramConfig for background colors (None uses defaults)
        ideal_length_factor: Multiplier for ideal node distance (default: 1.6)

    Returns:
        draw.io XML string of the ER diagram
    """
    diagram = _create_diagram(
        'drawio', schema_manager, schema_name, center_tables, referenced_by_level, references_level,
        category, diagram_config, ideal_length_factor
    )
    return diagram.render_drawio()


def generate_svg(
    schema_path: str,
    output_path: str,
    schema_name: str | None = None,
    center_tables: list[str] | None = None,
    referenced_by_level: int = 1,
    references_level: int = 1,
    category: str | None = None,
    project_path: str | None = None,
    ideal_length_factor: float = 1.6
) -> str:
    """
    Generate SVG ER diagram from a schema file.

    This function serves as the entry point for the dbgear svg plugin.

    Args:
        schema_path: Path to the schema.yaml file.
        output_path: Path to write the SVG file.
        schema_name: Name of the schema (uses first schema if None).
        center_tables: Tables to center diagram on (all tables if None or empty).
        referenced_by_level: Levels of tables that reference these tables to include.
        references_level: Levels of tables these tables reference to include.
        category: Filter tables by category (None for all tables).
        project_path: Path to project directory for diagram.yaml (uses schema_path parent if None).

    Returns:
        Path to the generated SVG file.
    """
    schema_manager = SchemaManager.load(schema_path)

    # Use first schema if not specified
    if schema_name is None:
        schema_name = next(iter(schema_manager.schemas.keys()))

    # Load diagram config
    if project_path is None:
        project_path = Path(schema_path).parent
    diagram_config = load_diagram_config(project_path)

    svg_content = generate_er_diagram_svg(
        schema_manager, schema_name, center_tables, referenced_by_level, references_level,
        category, diagram_config, ideal_length_factor
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    return output_path


def generate_drawio(
    schema_path: str,
    output_path: str,
    schema_name: str | None = None,
    center_tables: list[str] | None = None,
    referenced_by_level: int = 1,
    references_level: int = 1,
    category: str | None = None,
    project_path: str | None = None,
    ideal_length_factor: float = 1.6
) -> str:
    """
    Generate draw.io ER diagram from a schema file.

    This function serves as the entry point for the dbgear drawio plugin.

    Args:
        schema_path: Path to the schema.yaml file.
        output_path: Path to write the draw.io XML file.
        schema_name: Name of the schema (uses first schema if None).
        center_tables: Tables to center diagram on (all tables if None or empty).
        referenced_by_level: Levels of tables that reference these tables to include.
        references_level: Levels of tables these tables reference to include.
        category: Filter tables by category (None for all tables).
        project_path: Path to project directory for diagram.yaml (uses schema_path parent if None).

    Returns:
        Path to the generated draw.io file.
    """
    schema_manager = SchemaManager.load(schema_path)

    # Use first schema if not specified
    if schema_name is None:
        schema_name = next(iter(schema_manager.schemas.keys()))

    # Load diagram config
    if project_path is None:
        project_path = Path(schema_path).parent
    diagram_config = load_diagram_config(project_path)

    drawio_content = generate_er_diagram_drawio(
        schema_manager, schema_name, center_tables, referenced_by_level, references_level,
        category, diagram_config, ideal_length_factor
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(drawio_content)

    return output_path
