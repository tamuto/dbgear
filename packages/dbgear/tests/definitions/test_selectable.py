import unittest
from dbgear.core.definitions.selectable import retrieve


class TestSelectableDefinitions(unittest.TestCase):
    """Test cases for selectable definition parser"""

    def test_retrieve_basic_functionality(self):
        """Test basic selectable retrieval functionality"""
        test_items = {
            'y_or_n': 'Yes or No',
            'property_keys': 'Property Keys',
            'status_list': 'Status Options'
        }

        schemas = retrieve(
            folder='test_folder',
            prefix='_select',
            items=test_items
        )

        # Should return one schema
        self.assertEqual(len(schemas), 1)

        schema = list(schemas.values())[0]
        self.assertEqual(schema.name, '_select')  # Schema name is the prefix

        # Should have three tables (one for each item)
        self.assertEqual(len(schema.tables), 3)

        table_names = list(schema.tables.keys())
        self.assertIn('y_or_n', table_names)
        self.assertIn('property_keys', table_names)
        self.assertIn('status_list', table_names)

    def test_table_structure(self):
        """Test that generated tables have correct structure"""
        test_items = {
            'test_table': 'Test Table'
        }

        schemas = retrieve(
            folder='test_folder',
            prefix='_select',
            items=test_items
        )

        schema = list(schemas.values())[0]
        table = schema.tables['test_table']

        # Check table properties
        self.assertEqual(table.table_name, 'test_table')
        self.assertEqual(table.display_name, 'Test Table')

        # Should have exactly 2 fields
        self.assertEqual(len(table.fields), 2)

        # Check value field (should be primary key)
        value_field = table.fields[0]
        self.assertEqual(value_field.column_name, 'value')
        self.assertEqual(value_field.column_type, 'varchar')
        self.assertEqual(value_field.primary_key, 1)
        self.assertFalse(value_field.nullable)

        # Check caption field
        caption_field = table.fields[1]
        self.assertEqual(caption_field.column_name, 'caption')
        self.assertEqual(caption_field.column_type, 'varchar')
        self.assertIsNone(caption_field.primary_key)
        self.assertFalse(caption_field.nullable)

        # Should have no indexes
        self.assertEqual(len(table.indexes), 0)

    def test_multiple_items(self):
        """Test retrieval with multiple items"""
        test_items = {
            'colors': 'Color Options',
            'sizes': 'Size Options',
            'categories': 'Category List'
        }

        schemas = retrieve(
            folder='test_folder',
            prefix='_lookup',
            items=test_items
        )

        schema = list(schemas.values())[0]
        self.assertEqual(len(schema.tables), 3)

        # Check each table was created correctly
        for key, display_name in test_items.items():
            table = schema.tables[key]

            self.assertIsNotNone(table, f"Table {key} not found")
            self.assertEqual(table.display_name, display_name)
            self.assertEqual(len(table.fields), 2)

            # Check field structure is consistent
            value_field = table.fields[0]
            caption_field = table.fields[1]

            self.assertEqual(value_field.column_name, 'value')
            self.assertEqual(value_field.primary_key, 1)

            self.assertEqual(caption_field.column_name, 'caption')
            self.assertIsNone(caption_field.primary_key)

    def test_empty_items(self):
        """Test handling of empty items dictionary"""
        schemas = retrieve(
            folder='test_folder',
            prefix='_select',
            items={}
        )

        # Should return one schema with no tables
        self.assertEqual(len(schemas), 1)
        self.assertEqual(len(list(schemas.values())[0].tables), 0)

    def test_single_item(self):
        """Test handling of single item"""
        test_items = {
            'boolean': 'True/False'
        }

        schemas = retrieve(
            folder='test_folder',
            prefix='_flag',
            items=test_items
        )

        schema = list(schemas.values())[0]
        self.assertEqual(len(schema.tables), 1)

        table = schema.tables['boolean']
        self.assertEqual(table.table_name, 'boolean')
        self.assertEqual(table.display_name, 'True/False')
        self.assertEqual(len(table.fields), 2)

    def test_special_characters_in_names(self):
        """Test handling of special characters in item names and display names"""
        test_items = {
            'test_with_underscore': 'Test With Underscore',
            'test-with-dash': 'Test With Dash',
            'test.with.dots': 'Test With Dots',
            'japanese_name': '日本語テスト'
        }

        schemas = retrieve(
            folder='test_folder',
            prefix='_special',
            items=test_items
        )

        schema = list(schemas.values())[0]
        self.assertEqual(len(schema.tables), 4)

        # Check that all names are handled correctly
        expected_names = [
            'test_with_underscore',
            'test-with-dash',
            'test.with.dots',
            'japanese_name'
        ]

        actual_names = list(schema.tables.keys())
        for expected_name in expected_names:
            self.assertIn(expected_name, actual_names)

        # Check Japanese display name
        japanese_table = schema.tables['japanese_name']
        self.assertEqual(japanese_table.display_name, '日本語テスト')

    def test_prefix_variations(self):
        """Test different prefix values"""
        test_items = {'test': 'Test'}

        # Test with different prefixes
        prefixes = ['_select', '_lookup', 'prefix', '', '_']

        for prefix in prefixes:
            with self.subTest(prefix=prefix):
                schemas = retrieve(
                    folder='test_folder',
                    prefix=prefix,
                    items=test_items
                )

                schema = list(schemas.values())[0]
                table = schema.tables['test']

                # Table name is just the key, prefix is used as schema name
                self.assertEqual(table.table_name, 'test')

    def test_field_properties_detailed(self):
        """Test detailed field properties"""
        test_items = {'detailed_test': 'Detailed Test'}

        schemas = retrieve(
            folder='test_folder',
            prefix='_test',
            items=test_items
        )

        table = list(schemas.values())[0].tables['detailed_test']

        # Check value field details
        value_field = table.fields[0]
        self.assertEqual(value_field.column_name, 'value')
        self.assertEqual(value_field.column_type, 'varchar')
        self.assertEqual(value_field.primary_key, 1)
        self.assertFalse(value_field.nullable)
        self.assertIsNone(value_field.comment)
        self.assertIsNone(value_field.default_value)

        # Check caption field details
        caption_field = table.fields[1]
        self.assertEqual(caption_field.column_name, 'caption')
        self.assertEqual(caption_field.column_type, 'varchar')
        self.assertIsNone(caption_field.primary_key)
        self.assertFalse(caption_field.nullable)
        self.assertIsNone(caption_field.comment)
        self.assertIsNone(caption_field.default_value)

    def test_consistency_across_tables(self):
        """Test that all generated tables have consistent structure"""
        test_items = {
            'item1': 'Item One',
            'item2': 'Item Two',
            'item3': 'Item Three'
        }

        schemas = retrieve(
            folder='test_folder',
            prefix='_consistent',
            items=test_items
        )

        schema = list(schemas.values())[0]

        # All tables should have identical field structure
        for table_name, table in schema.tables.items():
            with self.subTest(table_name=table_name):
                self.assertEqual(len(table.fields), 2)

                value_field = table.fields[0]
                caption_field = table.fields[1]

                # Check value field consistency
                self.assertEqual(value_field.column_name, 'value')
                self.assertEqual(value_field.column_type, 'varchar')
                self.assertEqual(value_field.primary_key, 1)
                self.assertFalse(value_field.nullable)

                # Check caption field consistency
                self.assertEqual(caption_field.column_name, 'caption')
                self.assertEqual(caption_field.column_type, 'varchar')
                self.assertIsNone(caption_field.primary_key)
                self.assertFalse(caption_field.nullable)

                # No indexes should be present
                self.assertEqual(len(table.indexes), 0)


if __name__ == '__main__':
    unittest.main()
