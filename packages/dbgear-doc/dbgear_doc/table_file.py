"""
Table list file utilities.

A table list file enumerates table names, one per line.
Blank lines are ignored and ``#`` starts a comment.
Each entry may be qualified as ``schema.table``.
"""

from pathlib import Path


def read_table_file(path: str) -> list[str]:
    """Read table names from a file, skipping blank lines and ``#`` comments."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f'table file not found: {path}')

    names: list[str] = []
    with open(file_path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.split('#', 1)[0].strip()
            if line:
                names.append(line)
    return names


def qualify_table_name(name: str, default_schema: str) -> str:
    """Bind an unqualified table name to the default schema."""
    if '.' in name:
        return name
    return f'{default_schema}.{name}'
