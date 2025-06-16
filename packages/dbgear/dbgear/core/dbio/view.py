from . import engine
from ..models.schema import View


def is_exist(conn, env: str, view: View):
    """Check if view exists"""
    result = engine.select_one(
        conn,
        '''
        SELECT TABLE_NAME FROM information_schema.views
        WHERE table_schema = :env and table_name = :view_name
        ''',
        {'env': env, 'view_name': view.view_name})
    return result is not None


def drop(conn, env: str, view: View):
    """Drop view"""
    sql = f'DROP VIEW IF EXISTS {env}.{view.view_name}'
    engine.execute(conn, sql)


def create(conn, env: str, view: View):
    """Create view"""
    sql = f'CREATE VIEW {env}.{view.view_name} AS {view.select_statement}'
    engine.execute(conn, sql)


def create_or_replace(conn, env: str, view: View):
    """Create or replace view"""
    sql = f'CREATE OR REPLACE VIEW {env}.{view.view_name} AS {view.select_statement}'
    engine.execute(conn, sql)


def get_view_definition(conn, env: str, view_name: str):
    """Get view definition from database"""
    result = engine.select_one(
        conn,
        '''
        SELECT VIEW_DEFINITION FROM information_schema.views
        WHERE table_schema = :env and table_name = :view_name
        ''',
        {'env': env, 'view_name': view_name})
    return result['VIEW_DEFINITION'] if result else None


def validate_dependencies(conn, env: str, view: View):
    """Validate that all dependencies exist"""
    for dependency in view.get_dependencies():
        # Check if dependency is a table
        table_exists = engine.select_one(
            conn,
            '''
            SELECT TABLE_NAME FROM information_schema.tables
            WHERE table_schema = :env and table_name = :dependency
            ''',
            {'env': env, 'dependency': dependency})
        
        # Check if dependency is a view
        view_exists = engine.select_one(
            conn,
            '''
            SELECT TABLE_NAME FROM information_schema.views
            WHERE table_schema = :env and table_name = :dependency
            ''',
            {'env': env, 'dependency': dependency})
        
        if not table_exists and not view_exists:
            raise ValueError(f"Dependency '{dependency}' not found for view '{view.view_name}'")