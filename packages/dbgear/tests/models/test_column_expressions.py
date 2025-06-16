import tempfile
import unittest
import shutil
from pathlib import Path

from dbgear.core.models.schema_manager import SchemaManager, SchemaValidator
from dbgear.core.models.schema import Schema, Table, Field, Index


class TestColumnExpressions(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SchemaManager(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_expression_field_creation(self):
        """Test creating field with expression."""
        field = Field(
            column_name="full_name",
            display_name="Full Name",
            column_type="VARCHAR(101)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression="CONCAT(last_name, ' ', first_name)",
            stored=True,
            auto_increment=False,
            charset=None,
            collation=None
        )

        self.assertEqual(field.expression, "CONCAT(last_name, ' ', first_name)")
        self.assertTrue(field.stored)
        self.assertFalse(field.auto_increment)

    def test_auto_increment_field_creation(self):
        """Test creating field with auto increment."""
        field = Field(
            column_name="id",
            display_name="ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=True,
            charset=None,
            collation=None
        )

        self.assertTrue(field.auto_increment)
        self.assertEqual(field.primary_key, 1)
        self.assertFalse(field.nullable)

    def test_charset_collation_field_creation(self):
        """Test creating field with charset and collation."""
        field = Field(
            column_name="name",
            display_name="Name",
            column_type="VARCHAR(100)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=False,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )

        self.assertEqual(field.charset, "utf8mb4")
        self.assertEqual(field.collation, "utf8mb4_unicode_ci")

    def test_expression_field_validation_success(self):
        """Test successful validation of expression field."""
        field = Field(
            column_name="calculated_field",
            display_name="Calculated Field",
            column_type="VARCHAR(50)",
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression="UPPER(some_column)",
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertEqual(errors, [])

    def test_expression_field_validation_with_default_value(self):
        """Test validation fails when expression field has default value."""
        field = Field(
            column_name="calculated_field",
            display_name="Calculated Field",
            column_type="VARCHAR(50)",
            nullable=True,
            primary_key=None,
            default_value="some_default",
            foreign_key=None,
            comment=None,
            expression="UPPER(some_column)",
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertIn("Expression column cannot have default_value", errors)

    def test_expression_field_validation_as_primary_key(self):
        """Test validation fails when expression field is primary key."""
        field = Field(
            column_name="calculated_field",
            display_name="Calculated Field",
            column_type="VARCHAR(50)",
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression="UPPER(some_column)",
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertIn("Expression column cannot be primary key", errors)

    def test_expression_field_validation_as_foreign_key(self):
        """Test validation fails when expression field is foreign key."""
        field = Field(
            column_name="calculated_field",
            display_name="Calculated Field",
            column_type="VARCHAR(50)",
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key="other_table.id",
            comment=None,
            expression="UPPER(some_column)",
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertIn("Expression column cannot be foreign key", errors)

    def test_auto_increment_validation_success(self):
        """Test successful validation of auto increment field."""
        field = Field(
            column_name="id",
            display_name="ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=True,
            charset=None,
            collation=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertEqual(errors, [])

    def test_auto_increment_validation_without_primary_key(self):
        """Test validation fails when auto increment field is not primary key."""
        field = Field(
            column_name="id",
            display_name="ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=True,
            charset=None,
            collation=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertIn("AUTO_INCREMENT column must be part of primary key", errors)

    def test_auto_increment_validation_nullable(self):
        """Test validation fails when auto increment field is nullable."""
        field = Field(
            column_name="id",
            display_name="ID",
            column_type="BIGINT",
            nullable=True,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=True,
            charset=None,
            collation=None
        )

        errors = SchemaValidator.validate_field(field)
        self.assertIn("AUTO_INCREMENT column cannot be nullable", errors)

    def test_table_with_expression_fields(self):
        """Test creating table with expression fields."""
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
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=True,
                    charset=None,
                    collation=None
                ),
                Field(
                    column_name="first_name",
                    display_name="First Name",
                    column_type="VARCHAR(50)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=False,
                    charset="utf8mb4",
                    collation="utf8mb4_unicode_ci"
                ),
                Field(
                    column_name="last_name",
                    display_name="Last Name",
                    column_type="VARCHAR(50)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=False,
                    charset="utf8mb4",
                    collation="utf8mb4_unicode_ci"
                ),
                Field(
                    column_name="full_name",
                    display_name="Full Name",
                    column_type="VARCHAR(101)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression="CONCAT(last_name, ' ', first_name)",
                    stored=True,
                    auto_increment=False,
                    charset=None,
                    collation=None
                )
            ]
        )

        self.manager.add_table("test", table)

        retrieved_table = self.manager.get_table("test", "users")
        self.assertEqual(len(retrieved_table.fields), 4)

        # Check auto increment field
        id_field = retrieved_table.get_field("id")
        self.assertTrue(id_field.auto_increment)
        self.assertEqual(id_field.primary_key, 1)

        # Check charset/collation fields
        first_name_field = retrieved_table.get_field("first_name")
        self.assertEqual(first_name_field.charset, "utf8mb4")
        self.assertEqual(first_name_field.collation, "utf8mb4_unicode_ci")

        # Check expression field
        full_name_field = retrieved_table.get_field("full_name")
        self.assertEqual(full_name_field.expression, "CONCAT(last_name, ' ', first_name)")
        self.assertTrue(full_name_field.stored)

    def test_save_and_reload_with_expressions(self):
        """Test saving and reloading schema with expression fields."""
        # Create schema with expression fields
        schema = self.manager.create_schema("test")

        table = Table(
            instance="test",
            table_name="products",
            display_name="Products",
            fields=[
                Field(
                    column_name="id",
                    display_name="ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=1,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=True,
                    charset=None,
                    collation=None
                ),
                Field(
                    column_name="price",
                    display_name="Price",
                    column_type="DECIMAL(10,2)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=False,
                    charset=None,
                    collation=None
                ),
                Field(
                    column_name="tax_rate",
                    display_name="Tax Rate",
                    column_type="DECIMAL(5,4)",
                    nullable=False,
                    primary_key=None,
                    default_value="0.10",
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=False,
                    charset=None,
                    collation=None
                ),
                Field(
                    column_name="total_price",
                    display_name="Total Price",
                    column_type="DECIMAL(10,2)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression="price * (1 + tax_rate)",
                    stored=True,
                    auto_increment=False,
                    charset=None,
                    collation=None
                )
            ]
        )
        self.manager.add_table("test", table)

        # Save to file
        self.manager.save()

        # Create new manager and reload
        new_manager = SchemaManager(self.temp_dir)

        retrieved_table = new_manager.get_table("test", "products")
        self.assertEqual(len(retrieved_table.fields), 4)

        # Check auto increment field
        id_field = retrieved_table.get_field("id")
        self.assertTrue(id_field.auto_increment)

        # Check expression field
        total_price_field = retrieved_table.get_field("total_price")
        self.assertEqual(total_price_field.expression, "price * (1 + tax_rate)")
        self.assertTrue(total_price_field.stored)


if __name__ == '__main__':
    unittest.main()