import tempfile
import unittest
from pathlib import Path

from dbgear_doc.generator import generate_docs
from dbgear_doc.table_file import read_table_file, qualify_table_name


SCHEMA_YAML = """\
schemas:
  main:
    tables:
      users:
        displayName: Users
        columns:
        - columnName: id
          displayName: ID
          columnType:
            columnType: INT
            baseType: INT
          nullable: false
          primaryKey: 1
      orders:
        displayName: Orders
        columns:
        - columnName: id
          displayName: ID
          columnType:
            columnType: INT
            baseType: INT
          nullable: false
          primaryKey: 1
      products:
        displayName: Products
        columns:
        - columnName: id
          displayName: ID
          columnType:
            columnType: INT
            baseType: INT
          nullable: false
          primaryKey: 1
  audit:
    tables:
      logs:
        displayName: Logs
        columns:
        - columnName: id
          displayName: ID
          columnType:
            columnType: INT
            baseType: INT
          nullable: false
          primaryKey: 1
      users:
        displayName: Audit Users
        columns:
        - columnName: id
          displayName: ID
          columnType:
            columnType: INT
            baseType: INT
          nullable: false
          primaryKey: 1
"""

CONTEXT_TEMPLATE = """\
{% for f in table_files %}
{{ f.name }}={{ f.tables | join(',') }}
{% endfor %}
listed={{ listed_tables | sort | join(',') }}
"""

# Same as the usage example in tmplspec.md
UNLISTED_TEMPLATE = """\
{% for schema_name, schema in schemas.items() %}
{% set unlisted = [] %}
{% for table_name in schema.tables.tables | sort %}
{% if (schema_name ~ '.' ~ table_name) not in listed_tables %}
{% set _ = unlisted.append(table_name) %}
{% endif %}
{% endfor %}
{% if unlisted %}
## {{ schema_name }}: リスト未掲載テーブル
{% for table_name in unlisted %}
- {{ table_name }}
{% endfor %}
{% endif %}
{% endfor %}
"""


class TestReadTableFile(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_skips_blank_lines_and_comments(self):
        path = self.dir / 'list.txt'
        path.write_text('# title\nusers\n\n  orders  # inline\naudit.logs\n', encoding='utf-8')
        self.assertEqual(read_table_file(str(path)), ['users', 'orders', 'audit.logs'])

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_table_file(str(self.dir / 'missing.txt'))

    def test_qualify_table_name(self):
        self.assertEqual(qualify_table_name('users', 'main'), 'main.users')
        self.assertEqual(qualify_table_name('audit.logs', 'main'), 'audit.logs')


class TestGenerateDocsWithTableFiles(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.schema_path = self.dir / 'schema.yaml'
        self.schema_path.write_text(SCHEMA_YAML, encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name: str, content: str) -> str:
        path = self.dir / name
        path.write_text(content, encoding='utf-8')
        return str(path)

    def _render_schema(self, template: str, **kwargs) -> str:
        template_path = self._write('tmpl.txt.j2', template)
        output = self.dir / 'out' / 'index.txt'
        generate_docs(str(self.schema_path), str(output), template_path, scope='schema', **kwargs)
        return output.read_text(encoding='utf-8')

    def test_without_table_files(self):
        content = self._render_schema(CONTEXT_TEMPLATE)
        self.assertEqual(content, 'listed=\n')

    def test_table_files_context(self):
        first = self._write('first.txt', '# first\nusers\norders\nusers\n')
        second = self._write('second.txt', 'audit.logs\norders\n')
        content = self._render_schema(CONTEXT_TEMPLATE, table_files=[first, second])
        self.assertEqual(
            content,
            'first.txt=main.users,main.orders\n'
            'second.txt=audit.logs,main.orders\n'
            'listed=audit.logs,main.orders,main.users\n'
        )

    def test_schema_name_binds_unqualified_names(self):
        table_file = self._write('list.txt', 'users\n')
        content = self._render_schema(CONTEXT_TEMPLATE, table_files=[table_file], schema_name='audit')
        self.assertIn('listed=audit.users\n', content)

    def test_unknown_schema_name(self):
        table_file = self._write('list.txt', 'users\n')
        with self.assertRaises(ValueError):
            self._render_schema(CONTEXT_TEMPLATE, table_files=[table_file], schema_name='missing')

    def test_unknown_table_warns_and_continues(self):
        table_file = self._write('list.txt', 'users\nmissing_table\n')
        with self.assertLogs(level='WARNING') as logs:
            content = self._render_schema(CONTEXT_TEMPLATE, table_files=[table_file])
        self.assertIn('main.missing_table', logs.output[0])
        self.assertIn('listed=main.missing_table,main.users\n', content)

    def test_unlisted_tables_example(self):
        table_file = self._write('list.txt', 'users\naudit.logs\n')
        content = self._render_schema(UNLISTED_TEMPLATE, table_files=[table_file])
        self.assertEqual(
            content,
            '## main: リスト未掲載テーブル\n'
            '- orders\n'
            '- products\n'
            '## audit: リスト未掲載テーブル\n'
            '- users\n'
        )

    def test_table_scope_receives_listed_tables(self):
        table_file = self._write('list.txt', 'orders\n')
        template_path = self._write(
            'table.txt.j2',
            "{{ 'listed' if (schema_name ~ '.' ~ table_name) in listed_tables else 'unlisted' }}\n",
        )
        output_dir = self.dir / 'tables'
        generate_docs(
            str(self.schema_path), str(output_dir), template_path,
            scope='table', table_files=[table_file],
        )
        self.assertEqual((output_dir / 'main' / 'orders.txt').read_text(encoding='utf-8'), 'listed\n')
        self.assertEqual((output_dir / 'main' / 'users.txt').read_text(encoding='utf-8'), 'unlisted\n')
        self.assertEqual((output_dir / 'audit' / 'users.txt').read_text(encoding='utf-8'), 'unlisted\n')


if __name__ == '__main__':
    unittest.main()
