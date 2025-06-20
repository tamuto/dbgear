import tempfile
import unittest

from dbgear.core.models.schema import SchemaManager
from dbgear.core.models.schema import Schema, Table, Column


class TestSchemaManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SchemaManager()

    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_add_schema(self):
        """Test schema creation."""
        s = Schema(name="test")
        self.manager.add_schema(s)

        self.assertEqual(s.name, "test")
        self.assertTrue(self.manager.schema_exists("test"))
        self.assertEqual(self.manager.get_schema("test"), s)

    def test_add_duplicate_schema(self):
        """Test adding duplicate schema raises error."""
        self.manager.add_schema(Schema(name="test"))

        with self.assertRaises(ValueError) as context:
            self.manager.add_schema(Schema(name="test"))

        self.assertIn("already exists", str(context.exception))

    def test_remove_schema(self):
        """Test schema removal."""
        self.manager.add_schema(Schema(name="test"))
        self.assertTrue(self.manager.schema_exists("test"))

        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            columns=[
                Column(
                    column_name="id",
                    display_name="ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=1,
                    default_value=None,
                    foreign_key=None,
                    comment=None
                )
            ]
        )
        self.manager.get_schema("test").add_table(table)
        self.assertTrue(self.manager.get_schema("test").table_exists("users"))

        self.manager.remove_schema("test")
        self.assertFalse(self.manager.schema_exists("test"))

    def test_get_schemas(self):
        """Test getting all schemas."""
        self.manager.add_schema(Schema(name="schema1"))
        self.manager.add_schema(Schema(name="schema2"))

        schemas = self.manager.get_schemas()
        self.assertEqual(len(schemas), 2)
        self.assertIn("schema1", schemas)
        self.assertIn("schema2", schemas)

    def test_get_nonexistent_schema(self):
        """Test getting non-existent schema raises error."""
        with self.assertRaises(KeyError) as context:
            self.manager.get_schema("nonexistent")

        self.assertIn("'nonexistent'", str(context.exception))

    def test_remove_nonexistent_schema(self):
        """Test removing non-existent schema raises error."""
        with self.assertRaises(KeyError) as context:
            self.manager.remove_schema("nonexistent")

        self.assertIn("Schema 'nonexistent' not found", str(context.exception))


if __name__ == '__main__':
    unittest.main()
