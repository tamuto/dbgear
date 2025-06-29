import unittest
from dbgear.models.column_type import ColumnType, ColumnTypeItem, parse_column_type, create_simple_column_type


class TestColumnTypeItem(unittest.TestCase):

    def test_create_from_string(self):
        item = ColumnTypeItem.from_string("active")
        self.assertEqual(item.value, "active")
        self.assertEqual(item.caption, "active")
        self.assertIsNone(item.caption_)
        self.assertIsNone(item.description)

    def test_create_from_dict(self):
        item = ColumnTypeItem.from_dict({
            "value": "active",
            "caption": "Active Status",
            "description": "Indicates if the record is currently active"
        })
        self.assertEqual(item.value, "active")
        self.assertEqual(item.caption_, "Active Status")
        self.assertEqual(item.caption, "Active Status")
        self.assertEqual(item.description, "Indicates if the record is currently active")


class TestColumnType(unittest.TestCase):

    def test_enum_with_column_type_items(self):
        item1 = ColumnTypeItem(value="active", caption="Active")
        item2 = ColumnTypeItem(value="inactive", caption="Inactive", description="Not currently active")

        column_type = ColumnType(
            column_type="ENUM('active','inactive')",
            base_type="ENUM",
            items=[item1, item2]
        )

        self.assertEqual(len(column_type.items), 2)
        self.assertEqual(column_type.items[0].value, "active")
        self.assertEqual(column_type.items[0].caption, "Active")
        self.assertEqual(column_type.items[1].value, "inactive")
        self.assertEqual(column_type.items[1].description, "Not currently active")

    def test_get_item_values(self):
        item1 = ColumnTypeItem(value="yes", caption="Yes")
        item2 = ColumnTypeItem(value="no", caption="No")

        column_type = ColumnType(
            column_type="ENUM('yes','no')",
            base_type="ENUM",
            items=[item1, item2]
        )

        values = column_type.get_item_values()
        self.assertEqual(values, ["yes", "no"])

    def test_add_item_string(self):
        column_type = ColumnType(
            column_type="ENUM",
            base_type="ENUM"
        )

        column_type.add_item("test")
        self.assertEqual(len(column_type.items), 1)
        self.assertEqual(column_type.items[0].value, "test")
        self.assertIsNone(column_type.items[0].caption_)

    def test_add_item_dict(self):
        column_type = ColumnType(
            column_type="ENUM",
            base_type="ENUM"
        )

        column_type.add_item({
            "value": "pending",
            "caption": "Pending Review",
            "description": "Waiting for approval"
        })

        self.assertEqual(len(column_type.items), 1)
        self.assertEqual(column_type.items[0].value, "pending")
        self.assertEqual(column_type.items[0].caption, "Pending Review")
        self.assertEqual(column_type.items[0].description, "Waiting for approval")

    def test_add_item_object(self):
        column_type = ColumnType(
            column_type="ENUM",
            base_type="ENUM"
        )

        item = ColumnTypeItem(value="completed", caption="Completed")
        column_type.add_item(item)

        self.assertEqual(len(column_type.items), 1)
        self.assertEqual(column_type.items[0].value, "completed")
        self.assertEqual(column_type.items[0].caption, "Completed")

    def test_remove_item(self):
        item1 = ColumnTypeItem(value="draft", caption="Draft")
        item2 = ColumnTypeItem(value="published", caption="Published")

        column_type = ColumnType(
            column_type="ENUM('draft','published')",
            base_type="ENUM",
            items=[item1, item2]
        )

        # Remove existing item
        result = column_type.remove_item("draft")
        self.assertTrue(result)
        self.assertEqual(len(column_type.items), 1)
        self.assertEqual(column_type.items[0].value, "published")

        # Try to remove non-existing item
        result = column_type.remove_item("archived")
        self.assertFalse(result)
        self.assertEqual(len(column_type.items), 1)


class TestParseColumnType(unittest.TestCase):

    def test_parse_enum_to_column_type_items(self):
        column_type = parse_column_type("ENUM('small','medium','large')")

        self.assertEqual(column_type.base_type, "ENUM")
        self.assertEqual(len(column_type.items), 3)
        self.assertIsInstance(column_type.items[0], ColumnTypeItem)
        self.assertEqual(column_type.items[0].value, "small")
        self.assertEqual(column_type.items[1].value, "medium")
        self.assertEqual(column_type.items[2].value, "large")

    def test_parse_set_to_column_type_items(self):
        column_type = parse_column_type("SET('read','write','admin')")

        self.assertEqual(column_type.base_type, "SET")
        self.assertEqual(len(column_type.items), 3)
        self.assertIsInstance(column_type.items[0], ColumnTypeItem)
        self.assertEqual(column_type.items[0].value, "read")
        self.assertEqual(column_type.items[1].value, "write")
        self.assertEqual(column_type.items[2].value, "admin")

    def test_parse_enum_with_colon_format(self):
        column_type = parse_column_type("ENUM('1:Active','2:Inactive','3:Pending')")

        self.assertEqual(column_type.base_type, "ENUM")
        self.assertEqual(len(column_type.items), 3)

        # Check first item
        self.assertEqual(column_type.items[0].value, "1")
        self.assertEqual(column_type.items[0].caption, "Active")

        # Check second item
        self.assertEqual(column_type.items[1].value, "2")
        self.assertEqual(column_type.items[1].caption, "Inactive")

        # Check third item
        self.assertEqual(column_type.items[2].value, "3")
        self.assertEqual(column_type.items[2].caption, "Pending")

    def test_parse_enum_mixed_format(self):
        column_type = parse_column_type("ENUM('simple','1:With Caption','another_simple','2:Another Caption')")

        self.assertEqual(column_type.base_type, "ENUM")
        self.assertEqual(len(column_type.items), 4)

        # Simple value (no colon)
        self.assertEqual(column_type.items[0].value, "simple")
        self.assertEqual(column_type.items[0].caption, "simple")

        # Value with caption
        self.assertEqual(column_type.items[1].value, "1")
        self.assertEqual(column_type.items[1].caption, "With Caption")

        # Another simple value
        self.assertEqual(column_type.items[2].value, "another_simple")
        self.assertIsNone(column_type.items[2].caption_)

        # Another value with caption
        self.assertEqual(column_type.items[3].value, "2")
        self.assertEqual(column_type.items[3].caption, "Another Caption")

    def test_parse_enum_with_multiple_colons(self):
        column_type = parse_column_type("ENUM('url:http://example.com','email:user@domain.com')")

        self.assertEqual(column_type.base_type, "ENUM")
        self.assertEqual(len(column_type.items), 2)

        # First item: only first colon splits value and caption
        self.assertEqual(column_type.items[0].value, "url")
        self.assertEqual(column_type.items[0].caption, "http://example.com")

        # Second item: only first colon splits value and caption
        self.assertEqual(column_type.items[1].value, "email")
        self.assertEqual(column_type.items[1].caption, "user@domain.com")


class TestCreateSimpleColumnType(unittest.TestCase):

    def test_create_enum_with_strings(self):
        column_type = create_simple_column_type(
            'ENUM',
            items=['new', 'processing', 'completed']
        )

        self.assertEqual(column_type.base_type, "ENUM")
        self.assertEqual(column_type.column_type, "ENUM('new', 'processing', 'completed')")
        self.assertEqual(len(column_type.items), 3)
        self.assertIsInstance(column_type.items[0], ColumnTypeItem)
        self.assertEqual(column_type.items[0].value, "new")

    def test_create_enum_with_dicts(self):
        column_type = create_simple_column_type(
            'ENUM',
            items=[
                {'value': 'low', 'caption': 'Low Priority'},
                {'value': 'high', 'caption': 'High Priority', 'description': 'Urgent task'}
            ]
        )

        self.assertEqual(column_type.base_type, "ENUM")
        self.assertEqual(len(column_type.items), 2)
        self.assertEqual(column_type.items[0].value, "low")
        self.assertEqual(column_type.items[0].caption, "Low Priority")
        self.assertEqual(column_type.items[1].value, "high")
        self.assertEqual(column_type.items[1].description, "Urgent task")

    def test_create_enum_with_mixed_items(self):
        item_obj = ColumnTypeItem(value="custom", caption="Custom Status")
        column_type = create_simple_column_type(
            'ENUM',
            items=[
                'simple',
                {'value': 'complex', 'caption': 'Complex Item'},
                item_obj
            ]
        )

        self.assertEqual(len(column_type.items), 3)
        self.assertEqual(column_type.items[0].value, "simple")
        self.assertEqual(column_type.items[1].value, "complex")
        self.assertEqual(column_type.items[1].caption, "Complex Item")
        self.assertEqual(column_type.items[2].value, "custom")
        self.assertEqual(column_type.items[2].caption, "Custom Status")


if __name__ == '__main__':
    unittest.main()
