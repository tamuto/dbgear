"""
Schema importers package.

This package contains modules that implement schema importers for various formats.
Each importer module should implement a 'retrieve' function with the following signature:

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
    pass

Available importers:
- a5sql_mk2: Import from A5:SQL Mk-2 (.a5er) files
"""