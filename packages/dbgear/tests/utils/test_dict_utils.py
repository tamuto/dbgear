"""Unit tests for dict_utils module."""

import unittest
from dbgear.utils.dict_utils import dict_to_nested


class TestDictToNested(unittest.TestCase):
    """Test cases for dict_to_nested function."""

    def test_basic_nesting(self):
        """Test basic dot-notation key nesting."""
        input_dict = {
            "abc": "123",
            "col.aaa": None,
            "col.bbb": "222",
            "test.key": None
        }
        expected = {
            "abc": "123",
            "col": {
                "aaa": None,
                "bbb": "222"
            },
            "test": {
                "key": None
            }
        }
        result = dict_to_nested(input_dict)
        self.assertEqual(result, expected)

    def test_deep_nesting(self):
        """Test deep nested structure."""
        input_dict = {
            "a.b.c.d": "value1",
            "a.b.e": "value2",
            "a.f": "value3",
            "g": "value4"
        }
        expected = {
            "a": {
                "b": {
                    "c": {
                        "d": "value1"
                    },
                    "e": "value2"
                },
                "f": "value3"
            },
            "g": "value4"
        }
        result = dict_to_nested(input_dict)
        self.assertEqual(result, expected)

    def test_no_nesting(self):
        """Test dictionary without dot notation."""
        input_dict = {
            "abc": "123",
            "def": "456",
            "ghi": "789"
        }
        expected = {
            "abc": "123",
            "def": "456",
            "ghi": "789"
        }
        result = dict_to_nested(input_dict)
        self.assertEqual(result, expected)

    def test_empty_dict(self):
        """Test empty dictionary."""
        input_dict = {}
        expected = {}
        result = dict_to_nested(input_dict)
        self.assertEqual(result, expected)

    def test_custom_separator(self):
        """Test custom separator."""
        input_dict = {
            "abc": "123",
            "col/aaa": "111",
            "col/bbb": "222"
        }
        expected = {
            "abc": "123",
            "col": {
                "aaa": "111",
                "bbb": "222"
            }
        }
        result = dict_to_nested(input_dict, separator='/')
        self.assertEqual(result, expected)

    def test_mixed_values(self):
        """Test with different value types."""
        input_dict = {
            "str": "string_value",
            "num.int": 42,
            "num.float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3]
        }
        expected = {
            "str": "string_value",
            "num": {
                "int": 42,
                "float": 3.14
            },
            "bool": True,
            "none": None,
            "list": [1, 2, 3]
        }
        result = dict_to_nested(input_dict)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
