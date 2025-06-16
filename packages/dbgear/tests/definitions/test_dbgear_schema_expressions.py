import tempfile
import unittest
import os
import shutil
from pathlib import Path

from dbgear.core.definitions.dbgear_schema import retrieve, parse_field_definition
from dbgear.core.models.fileio import save_yaml


class TestDBGearSchemaExpressions(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_parse_expression_field(self):
        """Test parsing field with expression from YAML data."""
        field_data = {
            "column_name": "full_name",
            "display_name": "Full Name",
            "column_type": "VARCHAR(101)",
            "nullable": False,
            "expression": "CONCAT(last_name, ' ', first_name)",
            "stored": True
        }

        field = parse_field_definition(field_data)

        self.assertEqual(field.column_name, "full_name")
        self.assertEqual(field.expression, "CONCAT(last_name, ' ', first_name)")
        self.assertTrue(field.stored)
        self.assertFalse(field.auto_increment)

    def test_parse_auto_increment_field(self):
        """Test parsing field with auto increment from YAML data."""
        field_data = {
            "column_name": "id",
            "display_name": "ID",
            "column_type": "BIGINT",
            "nullable": False,
            "primary_key": 1,
            "auto_increment": True
        }

        field = parse_field_definition(field_data)

        self.assertEqual(field.column_name, "id")
        self.assertTrue(field.auto_increment)
        self.assertEqual(field.primary_key, 1)
        self.assertFalse(field.nullable)

    def test_parse_charset_collation_field(self):
        """Test parsing field with charset and collation from YAML data."""
        field_data = {
            "column_name": "name",
            "display_name": "Name",
            "column_type": "VARCHAR(100)",
            "nullable": False,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        }

        field = parse_field_definition(field_data)

        self.assertEqual(field.column_name, "name")
        self.assertEqual(field.charset, "utf8mb4")
        self.assertEqual(field.collation, "utf8mb4_unicode_ci")

    def test_parse_field_defaults(self):
        """Test parsing field with default values for new attributes."""
        field_data = {
            "column_name": "simple_field",
            "display_name": "Simple Field",
            "column_type": "VARCHAR(50)",
            "nullable": True
        }

        field = parse_field_definition(field_data)

        self.assertEqual(field.column_name, "simple_field")
        self.assertIsNone(field.expression)
        self.assertFalse(field.stored)
        self.assertFalse(field.auto_increment)
        self.assertIsNone(field.charset)
        self.assertIsNone(field.collation)

    def test_retrieve_schema_with_expressions(self):
        """Test retrieving complete schema with expression fields."""
        schema_data = {
            "schemas": {
                "main": {
                    "tables": {
                        "users": {
                            "display_name": "Users",
                            "fields": [
                                {
                                    "column_name": "id",
                                    "display_name": "ID",
                                    "column_type": "BIGINT",
                                    "nullable": False,
                                    "primary_key": 1,
                                    "auto_increment": True
                                },
                                {
                                    "column_name": "first_name",
                                    "display_name": "First Name",
                                    "column_type": "VARCHAR(50)",
                                    "nullable": False,
                                    "charset": "utf8mb4",
                                    "collation": "utf8mb4_unicode_ci"
                                },
                                {
                                    "column_name": "last_name",
                                    "display_name": "Last Name",
                                    "column_type": "VARCHAR(50)",
                                    "nullable": False,
                                    "charset": "utf8mb4",
                                    "collation": "utf8mb4_unicode_ci"
                                },
                                {
                                    "column_name": "full_name",
                                    "display_name": "Full Name",
                                    "column_type": "VARCHAR(101)",
                                    "nullable": False,
                                    "expression": "CONCAT(last_name, ' ', first_name)",
                                    "stored": True
                                },
                                {
                                    "column_name": "email_domain",
                                    "display_name": "Email Domain",
                                    "column_type": "VARCHAR(255)",
                                    "nullable": True,
                                    "expression": "SUBSTRING_INDEX(email, '@', -1)",
                                    "stored": False
                                }
                            ]
                        }
                    }
                }
            }
        }

        # Save schema data to temp file
        schema_file = os.path.join(self.temp_dir, "schema.yaml")
        save_yaml(schema_file, schema_data)

        # Retrieve schemas
        schemas = retrieve(self.temp_dir, "schema.yaml")

        self.assertIn("main", schemas)
        schema = schemas["main"]
        self.assertTrue(schema.table_exists("users"))

        table = schema.get_table("users")
        self.assertEqual(len(table.fields), 5)

        # Check auto increment field
        id_field = table.get_field("id")
        self.assertTrue(id_field.auto_increment)
        self.assertEqual(id_field.primary_key, 1)

        # Check charset/collation fields
        first_name_field = table.get_field("first_name")
        self.assertEqual(first_name_field.charset, "utf8mb4")
        self.assertEqual(first_name_field.collation, "utf8mb4_unicode_ci")

        # Check stored expression field
        full_name_field = table.get_field("full_name")
        self.assertEqual(full_name_field.expression, "CONCAT(last_name, ' ', first_name)")
        self.assertTrue(full_name_field.stored)

        # Check virtual expression field
        email_domain_field = table.get_field("email_domain")
        self.assertEqual(email_domain_field.expression, "SUBSTRING_INDEX(email, '@', -1)")
        self.assertFalse(email_domain_field.stored)

    def test_retrieve_schema_with_mapping_and_expressions(self):
        """Test retrieving schema with mapping and expression fields."""
        schema_data = {
            "schemas": {
                "dev": {
                    "tables": {
                        "products": {
                            "display_name": "Products",
                            "fields": [
                                {
                                    "column_name": "id",
                                    "display_name": "ID",
                                    "column_type": "BIGINT",
                                    "nullable": False,
                                    "primary_key": 1,
                                    "auto_increment": True
                                },
                                {
                                    "column_name": "price",
                                    "display_name": "Price",
                                    "column_type": "DECIMAL(10,2)",
                                    "nullable": False
                                },
                                {
                                    "column_name": "tax_rate",
                                    "display_name": "Tax Rate",
                                    "column_type": "DECIMAL(5,4)",
                                    "nullable": False,
                                    "default_value": "0.10"
                                },
                                {
                                    "column_name": "total_price",
                                    "display_name": "Total Price",
                                    "column_type": "DECIMAL(10,2)",
                                    "nullable": False,
                                    "expression": "price * (1 + tax_rate)",
                                    "stored": True
                                }
                            ]
                        }
                    }
                }
            }
        }

        # Save schema data to temp file
        schema_file = os.path.join(self.temp_dir, "schema.yaml")
        save_yaml(schema_file, schema_data)

        # Retrieve schemas with mapping
        mapping = {"dev": "production"}
        schemas = retrieve(self.temp_dir, "schema.yaml", mapping=mapping)

        self.assertIn("production", schemas)
        schema = schemas["production"]
        self.assertTrue(schema.table_exists("products"))

        table = schema.get_table("products")
        self.assertEqual(table.instance, "production")

        # Check expression field
        total_price_field = table.get_field("total_price")
        self.assertEqual(total_price_field.expression, "price * (1 + tax_rate)")
        self.assertTrue(total_price_field.stored)

    def test_complex_expressions(self):
        """Test parsing complex MySQL expressions."""
        field_data = {
            "column_name": "age_category",
            "display_name": "Age Category",
            "column_type": "VARCHAR(20)",
            "nullable": True,
            "expression": "CASE WHEN age < 20 THEN '未成年' WHEN age < 65 THEN '成人' ELSE '高齢者' END",
            "stored": True
        }

        field = parse_field_definition(field_data)

        expected_expression = "CASE WHEN age < 20 THEN '未成年' WHEN age < 65 THEN '成人' ELSE '高齢者' END"
        self.assertEqual(field.expression, expected_expression)
        self.assertTrue(field.stored)


if __name__ == '__main__':
    unittest.main()