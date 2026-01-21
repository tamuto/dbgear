"""
Document Generator for DBGear schemas.

This module provides the core functionality for generating
Markdown documentation from database schema definitions.
"""

from pathlib import Path

from dbgear.models.schema import SchemaManager


class DocumentGenerator:
    """
    Generates Markdown documentation from DBGear schema definitions.
    """

    def __init__(self, schema_manager: SchemaManager):
        """
        Initialize the document generator.

        Args:
            schema_manager: The schema manager containing database definitions.
        """
        self.schema_manager = schema_manager

    def generate(self, output_dir: Path) -> list[Path]:
        """
        Generate documentation files.

        Args:
            output_dir: Directory to write documentation files.

        Returns:
            List of generated file paths.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []

        # Generate index file
        index_path = output_dir / "index.md"
        self._generate_index(index_path)
        generated_files.append(index_path)

        # Generate documentation for each schema
        for schema_name, schema in self.schema_manager.schemas.items():
            schema_dir = output_dir / schema_name
            schema_dir.mkdir(parents=True, exist_ok=True)

            # Generate schema overview
            schema_path = schema_dir / "README.md"
            self._generate_schema_doc(schema_path, schema_name, schema)
            generated_files.append(schema_path)

            # Generate table documentation
            for table_name, table in schema.tables.tables.items():
                table_path = schema_dir / f"{table_name}.md"
                self._generate_table_doc(table_path, schema_name, table_name, table)
                generated_files.append(table_path)

        return generated_files

    def _generate_index(self, path: Path) -> None:
        """Generate the main index file."""
        lines = [
            "# Database Documentation",
            "",
            "## Schemas",
            "",
        ]

        for schema_name in self.schema_manager.schemas:
            lines.append(f"- [{schema_name}](./{schema_name}/README.md)")

        path.write_text("\n".join(lines), encoding="utf-8")

    def _generate_schema_doc(self, path: Path, schema_name: str, schema) -> None:
        """Generate documentation for a schema."""
        lines = [
            f"# Schema: {schema_name}",
            "",
        ]

        if schema.tables:
            lines.extend([
                "## Tables",
                "",
                "| Table Name | Description |",
                "|------------|-------------|",
            ])

            for table_name, table in schema.tables.tables.items():
                note = ""
                if hasattr(table, "notes") and table.notes:
                    note = table.notes.note if hasattr(table.notes, "note") else str(table.notes)
                    note = note.replace("\n", " ")[:50]
                    if len(note) == 50:
                        note += "..."
                lines.append(f"| [{table_name}](./{table_name}.md) | {note} |")

            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")

    def _generate_table_doc(self, path: Path, schema_name: str, table_name: str, table) -> None:
        """Generate documentation for a table."""
        lines = [
            f"# Table: {table_name}",
            "",
            f"**Schema:** {schema_name}",
            "",
        ]

        # Table notes/description
        if hasattr(table, "notes") and table.notes:
            note = table.notes.note if hasattr(table.notes, "note") else str(table.notes)
            lines.extend([
                "## Description",
                "",
                note,
                "",
            ])

        # Columns section
        if hasattr(table, "columns") and table.columns:
            lines.extend([
                "## Columns",
                "",
                "| Column | Type | Nullable | Default | Description |",
                "|--------|------|----------|---------|-------------|",
            ])

            for col in table.columns:
                col_name = col.column_name
                col_type = str(col.column_type) if col.column_type else ""
                nullable = "YES" if col.nullable else "NO"
                default = col.default_value if hasattr(col, "default_value") and col.default_value else ""
                note = ""
                if hasattr(col, "notes") and col.notes:
                    note = col.notes.note if hasattr(col.notes, "note") else str(col.notes)
                    note = note.replace("\n", " ")

                lines.append(f"| {col_name} | {col_type} | {nullable} | {default} | {note} |")

            lines.append("")

        # Primary Key section
        if hasattr(table, "primary_key") and table.primary_key:
            pk_cols = ", ".join(table.primary_key)
            lines.extend([
                "## Primary Key",
                "",
                f"- {pk_cols}",
                "",
            ])

        # Indexes section
        if hasattr(table, "indexes") and table.indexes:
            lines.extend([
                "## Indexes",
                "",
                "| Index Name | Columns | Unique |",
                "|------------|---------|--------|",
            ])

            for idx in table.indexes:
                idx_name = idx.index_name if hasattr(idx, "index_name") else ""
                columns = ", ".join(idx.columns) if hasattr(idx, "columns") else ""
                unique = "YES" if hasattr(idx, "unique") and idx.unique else "NO"
                lines.append(f"| {idx_name} | {columns} | {unique} |")

            lines.append("")

        # Foreign Keys section
        if hasattr(table, "foreign_keys") and table.foreign_keys:
            lines.extend([
                "## Foreign Keys",
                "",
                "| Constraint | Column | References |",
                "|------------|--------|------------|",
            ])

            for fk in table.foreign_keys:
                fk_name = fk.constraint_name if hasattr(fk, "constraint_name") else ""
                column = fk.column_name if hasattr(fk, "column_name") else ""
                ref_table = fk.ref_table if hasattr(fk, "ref_table") else ""
                ref_col = fk.ref_column if hasattr(fk, "ref_column") else ""
                lines.append(f"| {fk_name} | {column} | {ref_table}.{ref_col} |")

            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")


def generate_docs(
    schema_path: str,
    output_dir: str,
) -> list[Path]:
    """
    Generate documentation from a schema file.

    This function serves as the entry point for the dbgear doc plugin.

    Args:
        schema_path: Path to the schema.yaml file.
        output_dir: Directory to write documentation files.

    Returns:
        List of generated file paths.
    """
    schema_manager = SchemaManager.load(schema_path)

    generator = DocumentGenerator(schema_manager)
    return generator.generate(Path(output_dir))
