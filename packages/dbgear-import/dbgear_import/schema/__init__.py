"""
Schema import modules.

All schema importers must implement the retrieve function:
    retrieve(folder: str, filename: str, mapping: dict, **kwargs) -> SchemaManager
"""