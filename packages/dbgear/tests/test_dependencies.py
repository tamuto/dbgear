import unittest
import tempfile
import os
import yaml
from pathlib import Path

from dbgear.models.schema import SchemaManager
from dbgear.models.dependencies import TableDependencyAnalyzer, DependencyItem


class TestTableDependencyAnalyzer(unittest.TestCase):
    """Test cases for TableDependencyAnalyzer"""

    def setUp(self):
        """Set up test fixtures"""
        # Create test schema data
        self.test_schema_data = {
            'schemas': {
                'main': {
                    'tables': {
                        'users': {
                            'displayName': 'Users',
                            'columns': [
                                {
                                    'columnName': 'id',
                                    'displayName': 'ID',
                                    'columnType': {'columnType': 'VARCHAR(36)', 'baseType': 'VARCHAR', 'length': 36},
                                    'nullable': False,
                                    'primaryKey': 0
                                },
                                {
                                    'columnName': 'name',
                                    'displayName': 'Name',
                                    'columnType': {'columnType': 'VARCHAR(100)', 'baseType': 'VARCHAR', 'length': 100},
                                    'nullable': False
                                }
                            ]
                        },
                        'orders': {
                            'displayName': 'Orders',
                            'columns': [
                                {
                                    'columnName': 'id',
                                    'displayName': 'ID',
                                    'columnType': {'columnType': 'VARCHAR(36)', 'baseType': 'VARCHAR', 'length': 36},
                                    'nullable': False,
                                    'primaryKey': 0
                                },
                                {
                                    'columnName': 'user_id',
                                    'displayName': 'User ID',
                                    'columnType': {'columnType': 'VARCHAR(36)', 'baseType': 'VARCHAR', 'length': 36},
                                    'nullable': False
                                }
                            ],
                            'relations': [
                                {
                                    'target': {
                                        'schemaName': 'main',
                                        'tableName': 'users'
                                    },
                                    'bindColumns': [
                                        {
                                            'sourceColumn': 'user_id',
                                            'targetColumn': 'id'
                                        }
                                    ],
                                    'constraintName': 'FK_orders_users',
                                    'onDelete': 'CASCADE'
                                }
                            ]
                        },
                        'order_items': {
                            'displayName': 'Order Items',
                            'columns': [
                                {
                                    'columnName': 'id',
                                    'displayName': 'ID',
                                    'columnType': {'columnType': 'VARCHAR(36)', 'baseType': 'VARCHAR', 'length': 36},
                                    'nullable': False,
                                    'primaryKey': 0
                                },
                                {
                                    'columnName': 'order_id',
                                    'displayName': 'Order ID',
                                    'columnType': {'columnType': 'VARCHAR(36)', 'baseType': 'VARCHAR', 'length': 36},
                                    'nullable': False
                                }
                            ],
                            'relations': [
                                {
                                    'target': {
                                        'schemaName': 'main',
                                        'tableName': 'orders'
                                    },
                                    'bindColumns': [
                                        {
                                            'sourceColumn': 'order_id',
                                            'targetColumn': 'id'
                                        }
                                    ],
                                    'constraintName': 'FK_order_items_orders',
                                    'onDelete': 'CASCADE'
                                }
                            ]
                        }
                    }
                }
            }
        }
        
        # Create temporary schema file
        self.temp_dir = tempfile.mkdtemp()
        self.schema_file = os.path.join(self.temp_dir, 'test_schema.yaml')
        with open(self.schema_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.test_schema_data, f, allow_unicode=True, default_flow_style=False)
        
        # Create schema manager
        self.schema_manager = SchemaManager.load(self.schema_file)
        
        # Create test data directory structure
        self.project_folder = os.path.join(self.temp_dir, 'project')
        os.makedirs(os.path.join(self.project_folder, 'development', 'test'), exist_ok=True)
        
        # Create test data file
        test_data = [
            {'id': 'user1', 'name': 'Alice'},
            {'id': 'user2', 'name': 'Bob'}
        ]
        with open(os.path.join(self.project_folder, 'development', 'test', 'main@users.dat'), 'w', encoding='utf-8') as f:
            yaml.dump(test_data, f, allow_unicode=True, default_flow_style=False)
        
        # Initialize analyzer
        self.analyzer = TableDependencyAnalyzer(self.schema_manager, self.project_folder)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_analyze_basic_functionality(self):
        """Test basic dependency analysis functionality"""
        result = self.analyzer.analyze('main', 'users', left_level=1, right_level=1)
        
        # Check structure
        self.assertIn('target_table', result)
        self.assertIn('left', result)
        self.assertIn('right', result)
        
        # Check target table
        self.assertEqual(result['target_table']['schema_name'], 'main')
        self.assertEqual(result['target_table']['table_name'], 'users')
        
        # Check left dependencies (objects referencing users)
        self.assertIn('level_1', result['left'])
        left_level_1 = result['left']['level_1']
        self.assertEqual(len(left_level_1), 1)  # orders table should reference users
        
        relation_dep = left_level_1[0]
        self.assertEqual(relation_dep['type'], 'relation')
        self.assertEqual(relation_dep['schema_name'], 'main')
        self.assertEqual(relation_dep['table_name'], 'orders')
        self.assertEqual(relation_dep['object_name'], 'FK_orders_users')
        
        # Check right dependencies (objects referenced by users)
        self.assertIn('level_1', result['right'])
        right_level_1 = result['right']['level_1']
        self.assertEqual(len(right_level_1), 1)  # should have data source
        
        data_dep = right_level_1[0]
        self.assertEqual(data_dep['type'], 'data')

    def test_multi_level_dependencies(self):
        """Test multi-level dependency analysis"""
        result = self.analyzer.analyze('main', 'users', left_level=2, right_level=1)
        
        # Check level 1
        left_level_1 = result['left']['level_1']
        self.assertEqual(len(left_level_1), 1)  # orders
        
        # Check level 2 (should include order_items via orders)
        left_level_2 = result['left']['level_2']
        self.assertEqual(len(left_level_2), 1)  # order_items
        
        order_items_dep = left_level_2[0]
        self.assertEqual(order_items_dep['type'], 'relation')
        self.assertEqual(order_items_dep['table_name'], 'order_items')
        self.assertIn('path', order_items_dep)

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test invalid schema
        with self.assertRaises(ValueError) as cm:
            self.analyzer.analyze('invalid_schema', 'users')
        self.assertIn("Schema 'invalid_schema' not found", str(cm.exception))
        
        # Test invalid table
        with self.assertRaises(ValueError) as cm:
            self.analyzer.analyze('main', 'invalid_table')
        self.assertIn("Table 'invalid_table' not found", str(cm.exception))
        
        # Test invalid levels
        with self.assertRaises(ValueError) as cm:
            self.analyzer.analyze('main', 'users', left_level=5)
        self.assertIn("left_level must be between 0 and 3", str(cm.exception))
        
        with self.assertRaises(ValueError) as cm:
            self.analyzer.analyze('main', 'users', right_level=-1)
        self.assertIn("right_level must be between 0 and 3", str(cm.exception))

    def test_zero_level_dependencies(self):
        """Test zero level dependencies (no dependencies returned)"""
        result = self.analyzer.analyze('main', 'users', left_level=0, right_level=0)
        
        # Should have empty dependency lists
        self.assertEqual(result['left'], {})
        self.assertEqual(result['right'], {})

    def test_dependency_item_creation(self):
        """Test DependencyItem class functionality"""
        item = DependencyItem(
            dep_type='relation',
            schema_name='main',
            table_name='orders',
            object_name='FK_orders_users',
            details={'constraint_name': 'FK_orders_users'},
            path=[{'schema_name': 'main', 'table_name': 'users', 'relation_type': 'relation'}]
        )
        
        # Test properties
        self.assertEqual(item.type, 'relation')
        self.assertEqual(item.schema_name, 'main')
        self.assertEqual(item.table_name, 'orders')
        self.assertEqual(item.object_name, 'FK_orders_users')
        
        # Test to_dict conversion
        dict_result = item.to_dict()
        self.assertIn('type', dict_result)
        self.assertIn('schema_name', dict_result)
        self.assertIn('table_name', dict_result)
        self.assertIn('object_name', dict_result)
        self.assertIn('details', dict_result)
        self.assertIn('path', dict_result)

    def test_view_references_table(self):
        """Test view reference detection"""
        # Test simple table reference
        sql = "SELECT * FROM users WHERE id = 1"
        self.assertTrue(self.analyzer._view_references_table(sql, 'main', 'users'))
        
        # Test join reference
        sql = "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"
        self.assertTrue(self.analyzer._view_references_table(sql, 'main', 'users'))
        
        # Test no reference
        sql = "SELECT * FROM orders WHERE user_id = 1"
        self.assertFalse(self.analyzer._view_references_table(sql, 'main', 'users'))

    def test_data_source_detection(self):
        """Test data source file detection"""
        # Analyze table with data source
        result = self.analyzer.analyze('main', 'users', left_level=0, right_level=1)
        
        right_level_1 = result['right']['level_1']
        
        # Should find the data file we created
        data_deps = [dep for dep in right_level_1 if dep['type'] == 'data']
        self.assertGreater(len(data_deps), 0)
        
        data_dep = data_deps[0]
        self.assertEqual(data_dep['details']['environ'], 'development')
        self.assertEqual(data_dep['details']['record_count'], 2)

    def test_json_serialization(self):
        """Test that results can be serialized to JSON"""
        import json
        
        result = self.analyzer.analyze('main', 'users', left_level=1, right_level=1)
        
        # Should not raise an exception
        json_str = json.dumps(result, ensure_ascii=False)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 0)
        
        # Should be able to deserialize back
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized['target_table']['table_name'], 'users')


if __name__ == '__main__':
    unittest.main()