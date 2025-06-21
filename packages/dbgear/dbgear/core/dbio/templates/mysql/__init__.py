# flake8: noqa: D100
"""MySQL-specific SQL templates."""

from ..engine import template_engine


# CREATE TABLE template
CREATE_TABLE_TEMPLATE = """
CREATE TABLE {{ env }}.{{ table.table_name }} (
{%- for column in table.columns %}
  {{ column.column_name | escape_identifier }} {{ column.column_type.column_type if column.column_type.column_type else column.column_type }}
  {%- if column.column_type.length and column.column_type.length > 0 %}({{ column.column_type.length }}){% endif %}
  {%- if column.column_type.precision and column.column_type.scale %}({{ column.column_type.precision }}, {{ column.column_type.scale }}){% elif column.column_type.precision %}({{ column.column_type.precision }}){% endif %}
  {%- if not column.nullable %} NOT NULL{% endif %}
  {%- if column.auto_increment %} AUTO_INCREMENT{% endif %}
  {%- if column.expression %} GENERATED ALWAYS AS ({{ column.expression }}) {% if column.stored %}STORED{% else %}VIRTUAL{% endif %}{% elif column.default_value %} DEFAULT {{ column.default_value }}{% endif %}
  {%- if column.charset %} CHARACTER SET {{ column.charset }}{% endif %}
  {%- if column.collation %} COLLATE {{ column.collation }}{% endif %}
  {%- if column.notes and column.notes|length > 0 %} COMMENT {{ column.notes[0].content | escape_string }}{% endif %}
  {%- if not loop.last %},{% endif %}
{%- endfor %}
{%- set pk_columns = table.columns | selectattr('primary_key', 'ne', none) | sort(attribute='primary_key') | list %}
{%- if pk_columns %}
  , CONSTRAINT {{ table.table_name }}_PKC PRIMARY KEY ({{ pk_columns | map(attribute='column_name') | join_columns }})
{%- endif %}
{%- for relation in table.relations %}
  {%- if relation.constraint_name %}
  , CONSTRAINT {{ relation.constraint_name }}
    FOREIGN KEY ({{ relation.bind_columns | map(attribute='source_column') | join_columns }})
    REFERENCES {{ relation.target.table_name }} ({{ relation.bind_columns | map(attribute='target_column') | join_columns }})
    {%- if relation.on_delete != 'RESTRICT' %} ON DELETE {{ relation.on_delete }}{% endif %}
    {%- if relation.on_update != 'RESTRICT' %} ON UPDATE {{ relation.on_update }}{% endif %}
  {%- endif %}
{%- endfor %}
)
{%- if table.mysql_options %}
{%- if table.mysql_options.engine %} ENGINE={{ table.mysql_options.engine }}{% endif %}
{%- if table.mysql_options.charset %} DEFAULT CHARSET={{ table.mysql_options.charset }}{% endif %}
{%- if table.mysql_options.collation %} COLLATE={{ table.mysql_options.collation }}{% endif %}
{%- if table.mysql_options.auto_increment %} AUTO_INCREMENT={{ table.mysql_options.auto_increment }}{% endif %}
{%- if table.mysql_options.row_format %} ROW_FORMAT={{ table.mysql_options.row_format }}{% endif %}
{%- endif %}
"""

# CREATE INDEX template
CREATE_INDEX_TEMPLATE = """
CREATE {% if index.unique %}UNIQUE {% endif %}INDEX {{ index.index_name or (table.table_name + '_IX' + loop.index0|string) }}
{%- if index.index_type and index.index_type != 'BTREE' %} USING {{ index.index_type }}{% endif %}
 ON {{ env }}.{{ table.table_name }} ({{ index.columns | join_columns }})
{%- if index.partial_condition %} WHERE {{ index.partial_condition }}{% endif %}
"""

# CREATE VIEW template
CREATE_VIEW_TEMPLATE = """
CREATE VIEW {{ env }}.{{ view.view_name }} AS
{{ view.select_statement }}
"""

# CREATE DATABASE template
CREATE_DATABASE_TEMPLATE = """
CREATE DATABASE {{ database_name }}
{%- if charset %} DEFAULT CHARACTER SET {{ charset }}{% endif %}
{%- if collation %} COLLATE {{ collation }}{% endif %}
"""

# DROP DATABASE template
DROP_DATABASE_TEMPLATE = """
DROP DATABASE {{ database_name }}
"""

# Register templates
template_engine.add_template('mysql_create_table', CREATE_TABLE_TEMPLATE)
template_engine.add_template('mysql_create_index', CREATE_INDEX_TEMPLATE)
template_engine.add_template('mysql_create_view', CREATE_VIEW_TEMPLATE)
template_engine.add_template('mysql_create_database', CREATE_DATABASE_TEMPLATE)
template_engine.add_template('mysql_drop_database', DROP_DATABASE_TEMPLATE)
