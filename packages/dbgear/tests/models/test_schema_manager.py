import tempfile
import unittest
import os
from pathlib import Path

from dbgear.core.models.schema_manager import SchemaManager, SchemaValidator
from dbgear.core.models.schema import Schema, Table, Field, Index


class TestSchemaValidator(unittest.TestCase):

    def test_validate_table_success(self):
        """Test successful table validation."""
        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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

        errors = SchemaValidator.validate_table(table)
        self.assertEqual(errors, [])

    def test_validate_table_no_name(self):
        """Test table validation with missing name."""
        table = Table(
            instance="test",
            table_name="",
            display_name="Users",
            fields=[
                Field(
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

        errors = SchemaValidator.validate_table(table)
        self.assertIn("Table name is required", errors)

    def test_validate_table_no_fields(self):
        """Test table validation with no fields."""
        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[]
        )

        errors = SchemaValidator.validate_table(table)
        self.assertIn("Table must have at least one field", errors)

    def test_validate_field_success(self):
        """Test successful field validation."""
        field = Field(
            column_name="id",
            display_name="ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertEqual(errors, [])

    def test_validate_field_no_name(self):
        """Test field validation with missing name."""
        field = Field(
            column_name="",
            display_name="ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertIn("Column name is required", errors)

    def test_validate_foreign_key_success(self):
        """Test successful foreign key validation."""
        # Create schemas with referenced table
        schemas = {
            "main": Schema("main")
        }

        users_table = Table(
            instance="main",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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
        schemas["main"].add_table(users_table)

        field = Field(
            column_name="user_id",
            display_name="User ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key="users.id",
            comment=None
        )

        errors = SchemaValidator.validate_foreign_key(field, schemas)
        self.assertEqual(errors, [])

    def test_validate_foreign_key_table_not_found(self):
        """Test foreign key validation with missing referenced table."""
        schemas = {"main": Schema("main")}

        field = Field(
            column_name="user_id",
            display_name="User ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key="users.id",
            comment=None
        )

        errors = SchemaValidator.validate_foreign_key(field, schemas)
        self.assertIn("Referenced table 'users' not found", errors)


class TestSchemaManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SchemaManager(self.temp_dir)

    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_create_schema(self):
        """Test schema creation."""
        schema = self.manager.create_schema("test")

        self.assertEqual(schema.name, "test")
        self.assertTrue(self.manager.schema_exists("test"))
        self.assertEqual(self.manager.get_schema("test"), schema)

    def test_create_duplicate_schema(self):
        """Test creating duplicate schema raises error."""
        self.manager.create_schema("test")

        with self.assertRaises(ValueError) as context:
            self.manager.create_schema("test")

        self.assertIn("already exists", str(context.exception))

    def test_delete_schema(self):
        """Test schema deletion."""
        self.manager.create_schema("test")
        self.assertTrue(self.manager.schema_exists("test"))

        self.manager.delete_schema("test")
        self.assertFalse(self.manager.schema_exists("test"))

    def test_add_table(self):
        """Test adding table to schema."""
        schema = self.manager.create_schema("test")

        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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

        self.manager.add_table("test", table)

        retrieved_table = self.manager.get_table("test", "users")
        self.assertEqual(retrieved_table.table_name, "users")
        self.assertEqual(len(retrieved_table.fields), 1)

    def test_add_table_invalid(self):
        """Test adding invalid table raises error."""
        schema = self.manager.create_schema("test")

        # Table with no fields
        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[]
        )

        with self.assertRaises(ValueError) as context:
            self.manager.add_table("test", table)

        self.assertIn("validation failed", str(context.exception))

    def test_update_table(self):
        """Test updating existing table."""
        schema = self.manager.create_schema("test")

        # Add initial table
        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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
        self.manager.add_table("test", table)

        # Update table with new field
        updated_table = Table(
            instance="test",
            table_name="users",
            display_name="Updated Users",
            fields=[
                Field(
                    column_name="id",
                    display_name="ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=1,
                    default_value=None,
                    foreign_key=None,
                    comment=None
                ),
                Field(
                    column_name="name",
                    display_name="Name",
                    column_type="VARCHAR(100)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None
                )
            ]
        )

        self.manager.update_table("test", "users", updated_table)

        retrieved_table = self.manager.get_table("test", "users")
        self.assertEqual(retrieved_table.display_name, "Updated Users")
        self.assertEqual(len(retrieved_table.fields), 2)

    def test_delete_table(self):
        """Test deleting table."""
        schema = self.manager.create_schema("test")

        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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
        self.manager.add_table("test", table)

        self.manager.delete_table("test", "users")

        with self.assertRaises(KeyError):
            self.manager.get_table("test", "users")

    def test_add_field(self):
        """Test adding field to table."""
        schema = self.manager.create_schema("test")

        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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
        self.manager.add_table("test", table)

        new_field = Field(
            column_name="name",
            display_name="Name",
            column_type="VARCHAR(100)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None
        )

        self.manager.add_field("test", "users", new_field)

        retrieved_table = self.manager.get_table("test", "users")
        self.assertEqual(len(retrieved_table.fields), 2)
        self.assertTrue(retrieved_table.field_exists("name"))

    def test_foreign_key_validation(self):
        """Test foreign key validation across tables."""
        schema = self.manager.create_schema("test")

        # Add users table
        users_table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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
        self.manager.add_table("test", users_table)

        # Add posts table with foreign key to users
        posts_table = Table(
            instance="test",
            table_name="posts",
            display_name="Posts",
            fields=[
                Field(
                    column_name="id",
                    display_name="ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=1,
                    default_value=None,
                    foreign_key=None,
                    comment=None
                ),
                Field(
                    column_name="user_id",
                    display_name="User ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key="users.id",
                    comment=None
                )
            ]
        )

        # This should succeed
        self.manager.add_table("test", posts_table)

        retrieved_table = self.manager.get_table("test", "posts")
        user_id_field = retrieved_table.get_field("user_id")
        self.assertEqual(user_id_field.foreign_key, "users.id")

    def test_save_and_reload(self):
        """Test saving and reloading schemas."""
        # Create schema and table
        schema = self.manager.create_schema("test")

        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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
        self.manager.add_table("test", table)

        # Save to file
        self.manager.save()

        # Create new manager and reload
        new_manager = SchemaManager(self.temp_dir)

        self.assertTrue(new_manager.schema_exists("test"))
        retrieved_table = new_manager.get_table("test", "users")
        self.assertEqual(retrieved_table.table_name, "users")
        self.assertEqual(len(retrieved_table.fields), 1)

    def test_prevent_table_deletion_with_references(self):
        """Test preventing deletion of referenced table."""
        schema = self.manager.create_schema("test")

        # Add users table
        users_table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
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
        self.manager.add_table("test", users_table)

        # Add posts table with foreign key
        posts_table = Table(
            instance="test",
            table_name="posts",
            display_name="Posts",
            fields=[
                Field(
                    column_name="id",
                    display_name="ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=1,
                    default_value=None,
                    foreign_key=None,
                    comment=None
                ),
                Field(
                    column_name="user_id",
                    display_name="User ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key="users.id",
                    comment=None
                )
            ]
        )
        self.manager.add_table("test", posts_table)

        # Try to delete users table - should fail
        with self.assertRaises(ValueError) as context:
            self.manager.delete_table("test", "users")

        self.assertIn("referenced by", str(context.exception))


if __name__ == '__main__':
    unittest.main()
