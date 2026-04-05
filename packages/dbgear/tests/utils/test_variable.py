import unittest

from dbgear.utils.variable import expand_variables, expand_value, expand_dict


class TestExpandVariables(unittest.TestCase):
    """Test variable expansion in data items."""

    def setUp(self):
        self.settings = {
            'app_name': 'MyApplication',
            'base_url': 'https://example.com',
            'admin_email': 'admin@example.com',
        }

    def test_simple_expansion(self):
        items = [{'name': '$app_name'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['name'], 'MyApplication')

    def test_partial_expansion(self):
        items = [{'url': '$base_url/api/v1'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['url'], 'https://example.com/api/v1')

    def test_multiple_variables_in_one_value(self):
        items = [{'info': '$app_name - $admin_email'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['info'], 'MyApplication - admin@example.com')

    def test_undefined_variable_kept(self):
        items = [{'name': '$undefined'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['name'], '$undefined')

    def test_escape_with_double_dollar(self):
        items = [{'expr': '$$app_name'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['expr'], '$app_name')

    def test_escape_and_expand_mixed(self):
        items = [{'mixed': '$$base_url/$app_name'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['mixed'], '$base_url/MyApplication')

    def test_nested_dict_expansion(self):
        items = [{'metadata': {'title': '$app_name', 'url': '$base_url'}}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['metadata']['title'], 'MyApplication')
        self.assertEqual(result[0]['metadata']['url'], 'https://example.com')

    def test_non_string_values_unchanged(self):
        items = [{'id': 1, 'active': True, 'score': 3.14, 'empty': None}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[0]['active'], True)
        self.assertEqual(result[0]['score'], 3.14)
        self.assertIsNone(result[0]['empty'])

    def test_empty_settings_returns_original(self):
        items = [{'name': '$app_name'}]
        result = expand_variables(items, {})
        self.assertEqual(result[0]['name'], '$app_name')

    def test_multiple_items(self):
        items = [
            {'name': '$app_name', 'id': 1},
            {'name': '$app_name', 'id': 2},
        ]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['name'], 'MyApplication')
        self.assertEqual(result[1]['name'], 'MyApplication')

    def test_no_variable_in_value(self):
        items = [{'name': 'plain text'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['name'], 'plain text')

    def test_escape_undefined_variable(self):
        items = [{'expr': '$$unknown'}]
        result = expand_variables(items, self.settings)
        self.assertEqual(result[0]['expr'], '$unknown')


class TestExpandValue(unittest.TestCase):
    """Test expand_value edge cases."""

    def setUp(self):
        self.settings = {
            'app_name': 'MyApplication',
            'data_dir': '/opt/data',
        }

    def test_string_expansion(self):
        result = expand_value('$data_dir/master.xlsx', self.settings)
        self.assertEqual(result, '/opt/data/master.xlsx')

    def test_none_value(self):
        result = expand_value(None, self.settings)
        self.assertIsNone(result)

    def test_int_value(self):
        result = expand_value(42, self.settings)
        self.assertEqual(result, 42)

    def test_list_value_not_expanded(self):
        """Lists are not expanded (only str and dict are handled)."""
        result = expand_value(['$app_name', 'other'], self.settings)
        self.assertEqual(result, ['$app_name', 'other'])

    def test_dict_value(self):
        result = expand_value({'path': '$data_dir/file'}, self.settings)
        self.assertEqual(result, {'path': '/opt/data/file'})

    def test_escape_in_value(self):
        result = expand_value('$$app_name', self.settings)
        self.assertEqual(result, '$app_name')


class TestExpandDict(unittest.TestCase):
    """Test expand_dict for kwargs expansion."""

    def setUp(self):
        self.settings = {
            'data_dir': '/opt/data',
            'sheet_name': 'master',
        }

    def test_simple_dict(self):
        d = {'path': '$data_dir/file.xlsx', 'sheet': '$sheet_name'}
        result = expand_dict(d, self.settings)
        self.assertEqual(result['path'], '/opt/data/file.xlsx')
        self.assertEqual(result['sheet'], 'master')

    def test_non_string_values_preserved(self):
        d = {'header_row': 1, 'start_row': 2, 'path': '$data_dir/file'}
        result = expand_dict(d, self.settings)
        self.assertEqual(result['header_row'], 1)
        self.assertEqual(result['start_row'], 2)
        self.assertEqual(result['path'], '/opt/data/file')

    def test_empty_settings_returns_original(self):
        d = {'path': '$data_dir/file'}
        result = expand_dict(d, {})
        self.assertEqual(result['path'], '$data_dir/file')

    def test_empty_dict(self):
        result = expand_dict({}, self.settings)
        self.assertEqual(result, {})

    def test_escape_in_dict(self):
        d = {'expr': '$$data_dir', 'path': '$data_dir'}
        result = expand_dict(d, self.settings)
        self.assertEqual(result['expr'], '$data_dir')
        self.assertEqual(result['path'], '/opt/data')


if __name__ == '__main__':
    unittest.main()
