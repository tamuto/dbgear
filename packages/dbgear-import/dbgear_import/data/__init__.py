"""
Data import modules.

All data importers must implement the import_data function:
    import_data(source: str, schema: SchemaManager, table_name: str, output_path: str, 
                schema_name: str = 'main', json_fields: Optional[List[str]] = None, 
                **kwargs) -> str

Available importers:
    - excel: Excel file importer using openpyxl
    - csv: CSV file importer using standard csv library

Usage example:
    from dbgear_import.data.excel import import_data
    from dbgear.models.schema import SchemaManager
    
    schema = SchemaManager()
    schema.load('schema.yaml')
    
    output_file = import_data(
        'users.xlsx',
        schema,
        'users',
        'output_dir',
        'main',
        ['profile', 'settings']
    )
"""