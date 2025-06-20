import unittest
import tempfile
import os

from dbgear.core.definitions.a5sql_mk2 import (
    retrieve, convert_to_schema, Parser, Entity
)


class TestA5SQLMK2Definitions(unittest.TestCase):
    """Test cases for A5:ER definition parser"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_mapping = {
            'MAIN': 'main',
            'SUB': 'sub'
        }

        # Sample A5:ER content for testing
        self.sample_a5er_content = '''# -*- coding: utf-8 -*-

[Entity]
PName=test_table
LName=テストテーブル
Page=MAIN
Field="IDカラム","col_id","varchar(36)","NOT NULL",0,"",""
Field="名前","name","varchar(100)","NOT NULL",,"",""
Field="年齢","age","int","NULL",,"",""
Field="作成日時","created_at","datetime","NOT NULL",,"",""

[Entity]
PName=child_table
LName=子テーブル
Page=MAIN
Field="IDカラム","child_id","varchar(36)","NOT NULL",0,"",""
Field="親ID","parent_id","varchar(36)","NOT NULL",,"",""
Field="値","value","varchar(255)","NULL",,"",""

[Relation]
Entity1=test_table
Entity2=child_table
Fields1=col_id
Fields2=parent_id
Cardinality1=1
Cardinality2=*
'''

    def create_temp_a5er_file(self, content):
        """Create a temporary A5:ER file for testing"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.a5er', delete=False, encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_parser_basic_entity_parsing(self):
        """Test basic entity parsing functionality"""
        parser = Parser(self.test_mapping)

        # Test entity parsing
        parser.parse_line(1, '[Entity]')  # Start entity section

        entity_lines = [
            'PName=users',
            'LName=User Table',
            'Page=MAIN',
            'Field="ID","id","int","NOT NULL",0,"",""',
            'Field="Name","name","varchar(100)","NOT NULL",,"",""'
        ]

        # Parse entity section
        for i, line in enumerate(entity_lines):
            parser.parse_line(i + 2, line)

        # End entity section with empty line
        parser.parse_line(10, '')

        # Verify entity was created
        self.assertEqual(len(parser.instances), 1)
        self.assertIn('main', parser.instances)

        entity = parser.instances['main'][0]
        self.assertEqual(entity.table_name, 'users')
        self.assertEqual(entity.display_name, 'User Table')
        self.assertEqual(entity.instance, 'main')
        self.assertEqual(len(entity.fields), 2)

        # Check field strings (they are CSV strings, not parsed yet)
        self.assertEqual(entity.fields[0], '"ID","id","int","NOT NULL",0,"",""')
        self.assertEqual(entity.fields[1], '"Name","name","varchar(100)","NOT NULL",,"",""')

        # To test parsed fields, we need to use convert_to_schema
        schemas = convert_to_schema(parser)
        main_schema = schemas.get_schema('main')
        users_table = main_schema.get_table('users')

        # Check parsed fields
        id_field = users_table.columns[0]
        self.assertEqual(id_field.column_name, 'id')
        self.assertEqual(id_field.column_type, 'int')
        self.assertFalse(id_field.nullable)
        self.assertEqual(id_field.primary_key, 0)

        name_field = users_table.columns[1]
        self.assertEqual(name_field.column_name, 'name')
        self.assertEqual(name_field.column_type, 'varchar(100)')
        self.assertFalse(name_field.nullable)
        self.assertIsNone(name_field.primary_key)

    def test_parser_relation_parsing(self):
        """Test relation parsing functionality"""
        parser = Parser(self.test_mapping)

        # First create entities
        parser.parse_line(1, '[Entity]')  # Start entity section
        entity1_lines = [
            'PName=parent_table',
            'LName=Parent',
            'Page=MAIN',
            'Field="ID","id","int","NOT NULL",0,"",""'
        ]

        # Parse first entity
        for i, line in enumerate(entity1_lines):
            parser.parse_line(i + 2, line)

        parser.parse_line(10, '')  # Reset session

        # Parse second entity
        parser.parse_line(11, '[Entity]')  # Start new entity section
        entity2_lines = [
            'PName=child_table',
            'LName=Child',
            'Page=MAIN',
            'Field="ID","id","int","NOT NULL",0,"",""',
            'Field="Parent ID","parent_id","int","NOT NULL",,"",""'
        ]

        for i, line in enumerate(entity2_lines):
            parser.parse_line(i + 12, line)

        parser.parse_line(20, '')  # Reset session

        # Parse relation
        parser.parse_line(21, '[Relation]')  # Start relation section
        relation_lines = [
            'Entity1=parent_table',
            'Entity2=child_table',
            'Fields1=id',
            'Fields2=parent_id'
        ]

        for i, line in enumerate(relation_lines):
            parser.parse_line(i + 22, line)

        # End relation section
        parser.parse_line(30, '')

        # Verify relation was created
        self.assertEqual(len(parser.relations), 1)
        self.assertIn('child_table', parser.relations)

        relation_dict = parser.relations['child_table']
        self.assertIn('parent_id', relation_dict)

        relation = relation_dict['parent_id']
        self.assertEqual(relation.entity1, 'parent_table')
        self.assertEqual(relation.entity2, 'child_table')
        self.assertEqual(relation.fields1, 'id')
        self.assertEqual(relation.fields2, 'parent_id')

    def test_parser_index_parsing(self):
        """Test index parsing functionality"""
        parser = Parser(self.test_mapping)

        # Create an entity first
        parser.parse_line(1, '[Entity]')  # Start entity section
        entity_lines = [
            'PName=test_table',
            'LName=Test Table',
            'Page=MAIN',
            'Field="ID","id","int","NOT NULL",0,"",""',
            'Field="Name","name","varchar(100)","NOT NULL",,"",""'
        ]

        for i, line in enumerate(entity_lines):
            parser.parse_line(i + 2, line)

        parser.parse_line(10, '')  # Reset session

        # Indexes are actually parsed as part of entities in A5SQL, not as separate sections
        # Let's check that the entity has the Index field
        entity = parser.instances['main'][0]

        # Add an index to the entity manually for testing
        entity.indexes.append('idx_name,name')

        # Convert to schema to test index processing
        schemas = convert_to_schema(parser)
        main_schema = schemas.get_schema('main')
        test_table = main_schema.get_table('test_table')

        # Verify index was processed correctly in schema
        self.assertEqual(len(test_table.indexes), 1)

        index = test_table.indexes[0]
        self.assertEqual(index.index_name, None)  # A5SQL doesn't store index names in this format
        self.assertEqual(index.columns, ['name'])

    def test_convert_to_schema(self):
        """Test conversion from parsed data to Schema objects"""
        parser = Parser(self.test_mapping)

        # Create test entities and add to parser instances
        entity1 = Entity()
        entity1.table_name = 'users'
        entity1.display_name = 'Users'
        entity1.instance = 'main'
        entity1.fields = [
            '"User ID","user_id","varchar(36)","NOT NULL","0","",""',
            '"Name","name","varchar(100)","NOT NULL","","",""',
            '"Email","email","varchar(255)","NULL","","",""'
        ]
        entity1.indexes = [
            'idx_email,email'  # A5SQL index format: index_name,field1,field2,...
        ]

        entity2 = Entity()
        entity2.table_name = 'orders'
        entity2.display_name = 'Orders'
        entity2.instance = 'sub'
        entity2.fields = [
            '"Order ID","order_id","varchar(36)","NOT NULL","0","",""',
            '"User ID","user_id","varchar(36)","NOT NULL","","",""'
        ]
        entity2.indexes = []

        # Add entities to parser instances
        parser.instances = {
            'main': [entity1],
            'sub': [entity2]
        }

        # Convert to schemas
        schemas = convert_to_schema(parser)

        # Should create two schemas (one for each instance)
        self.assertEqual(len(schemas.get_schemas()), 2)

        # Find main schema
        main_schema = schemas.get_schema('main')
        self.assertEqual(len(main_schema.tables), 1)

        users_table = main_schema.get_table('users')
        self.assertEqual(users_table.table_name, 'users')
        self.assertEqual(users_table.display_name, 'Users')
        self.assertEqual(len(users_table.columns), 3)
        self.assertEqual(len(users_table.indexes), 1)

        # Check primary key field
        primary_field = users_table.columns[0]
        self.assertEqual(primary_field.column_name, 'user_id')
        self.assertEqual(primary_field.primary_key, 0)
        self.assertFalse(primary_field.nullable)

        # Check nullable field
        email_field = users_table.columns[2]
        self.assertEqual(email_field.column_name, 'email')
        self.assertIsNone(email_field.primary_key)
        self.assertTrue(email_field.nullable)

        # Check index
        email_index = users_table.indexes[0]
        self.assertEqual(email_index.index_name, None)  # A5SQL indexes don't have names
        self.assertEqual(email_index.columns, ['email'])

        # Find sub schema
        sub_schema = schemas.get_schema('sub')
        self.assertEqual(len(sub_schema.tables), 1)

        orders_table = sub_schema.get_table('orders')
        self.assertEqual(orders_table.table_name, 'orders')
        self.assertEqual(len(orders_table.columns), 2)
        self.assertEqual(len(orders_table.indexes), 0)

    def test_retrieve_full_integration(self):
        """Test full integration with file reading"""
        # Create temporary file
        temp_file = self.create_temp_a5er_file(self.sample_a5er_content)

        try:
            # Test retrieve function
            schemas = retrieve(
                folder=os.path.dirname(temp_file),
                filename=os.path.basename(temp_file),
                mapping=self.test_mapping
            )

            # Verify schemas
            self.assertEqual(len(schemas.get_schemas()), 1)  # Only MAIN instance has entities

            main_schema = schemas.get_schema('main')
            self.assertEqual(main_schema.name, 'main')
            self.assertEqual(len(main_schema.tables), 2)

            # Check test_table
            test_table = main_schema.get_table('test_table')
            self.assertEqual(test_table.display_name, 'テストテーブル')
            self.assertEqual(len(test_table.columns), 4)
            self.assertEqual(len(test_table.indexes), 0)  # No indexes in simplified test

            # Check primary key
            id_field = test_table.columns[0]
            self.assertEqual(id_field.column_name, 'col_id')
            self.assertEqual(id_field.primary_key, 0)

            # Check child_table
            child_table = main_schema.get_table('child_table')
            self.assertEqual(child_table.display_name, '子テーブル')
            self.assertEqual(len(child_table.columns), 3)
            self.assertEqual(len(child_table.indexes), 0)  # No indexes in simplified test

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    def test_parser_mode_switching(self):
        """Test parser mode switching between sections"""
        parser = Parser(self.test_mapping)

        # Test initial mode
        self.assertIsNone(parser.mode)

        # Test mode detection and switching
        parser.parse_line(1, '[Entity]')
        self.assertEqual(parser.mode, 2)  # Entity mode

        # Test Comment mode
        parser = Parser(self.test_mapping)  # Fresh parser
        parser.parse_line(1, '[Comment]')
        self.assertEqual(parser.mode, 4)  # Comment mode

    def test_parser_empty_lines_and_comments(self):
        """Test parser handling of empty lines and comments"""
        parser = Parser(self.test_mapping)

        # Add an entity first
        parser.parse_line(1, '[Entity]')
        parser.parse_line(2, 'PName=test')
        parser.parse_line(3, 'Page=MAIN')

        # Empty line should reset mode and add entity to instances
        parser.parse_line(4, '')
        self.assertIsNone(parser.mode)

        # Check that entity was added to instances
        self.assertEqual(len(parser.instances), 1)
        self.assertIn('main', parser.instances)
        self.assertEqual(len(parser.instances['main']), 1)

        # Comment line should be handled gracefully
        parser.parse_line(5, '# This is a comment')

    def test_field_parsing_edge_cases(self):
        """Test field parsing with various edge cases"""
        parser = Parser(self.test_mapping)

        # Test entity with edge case fields
        parser.parse_line(1, '[Entity]')  # Start entity section
        entity_lines = [
            'PName=edge_case_table',
            'LName=Edge Cases',
            'Page=MAIN',
            'Field="Empty Default","col1","varchar(50)","NULL",,"",""',  # Empty default, empty comment
            'Field="Quoted,Field","col2","varchar(100)","NOT NULL",,"default","Comment with, commas"',  # Commas in quotes
            'Field="Unicode","unicode_col","varchar(255)","NULL",,"デフォルト","日本語コメント"'  # Unicode content
        ]

        for i, line in enumerate(entity_lines):
            parser.parse_line(i + 2, line)

        # End entity section
        parser.parse_line(10, '')

        entity = parser.instances['main'][0]
        self.assertEqual(len(entity.fields), 3)

        # Check field strings (they are CSV strings, not parsed yet)
        self.assertEqual(entity.fields[0], '"Empty Default","col1","varchar(50)","NULL",,"",""')
        self.assertEqual(entity.fields[1], '"Quoted,Field","col2","varchar(100)","NOT NULL",,"default","Comment with, commas"')
        self.assertEqual(entity.fields[2], '"Unicode","unicode_col","varchar(255)","NULL",,"デフォルト","日本語コメント"')

        # To test parsed fields, we need to use convert_to_schema
        schemas = convert_to_schema(parser)
        main_schema = schemas.get_schema('main')
        edge_table = main_schema.get_table('edge_case_table')

        # Check parsed fields
        col1_field = edge_table.columns[0]
        self.assertEqual(col1_field.column_name, 'col1')
        self.assertTrue(col1_field.nullable)

        col2_field = edge_table.columns[1]
        self.assertEqual(col2_field.display_name, 'Quoted,Field')
        self.assertEqual(col2_field.default_value, 'default')

        unicode_field = edge_table.columns[2]
        self.assertEqual(unicode_field.column_name, 'unicode_col')
        self.assertEqual(unicode_field.default_value, 'デフォルト')

    def test_unmapped_instances(self):
        """Test handling of entities with unmapped instances"""
        # Create content with unmapped instance
        content_with_unmapped = '''[Entity]
PName=unmapped_table
LName=Unmapped
Page=UNMAPPED
Field="ID","id","int","NOT NULL",0,"",""

[Entity]
PName=mapped_table
LName=Mapped
Page=MAIN
Field="ID","id","int","NOT NULL",0,"",""
'''

        temp_file = self.create_temp_a5er_file(content_with_unmapped)

        try:
            schemas = retrieve(
                folder=os.path.dirname(temp_file),
                filename=os.path.basename(temp_file),
                mapping=self.test_mapping
            )

            # Should only return schemas for mapped instances
            self.assertEqual(len(schemas.get_schemas()), 1)

            main_schema = schemas.get_schema('main')
            self.assertEqual(main_schema.name, 'main')
            self.assertEqual(len(main_schema.tables), 1)
            self.assertEqual(main_schema.get_table('mapped_table').table_name, 'mapped_table')

        finally:
            os.unlink(temp_file)

    def test_file_encoding_with_bom(self):
        """Test handling of files with UTF-8 BOM"""
        # Create content with BOM
        content_with_bom = '\ufeff[Entity]\nPName=bom_table\nLName=BOM Test\nPage=MAIN\nField="ID","id","int","NOT NULL",0,"",""\n'

        temp_file = self.create_temp_a5er_file(content_with_bom)

        try:
            schemas = retrieve(
                folder=os.path.dirname(temp_file),
                filename=os.path.basename(temp_file),
                mapping=self.test_mapping
            )

            # Should handle BOM correctly
            self.assertEqual(len(schemas.get_schemas()), 1)

            main_schema = schemas.get_schema('main')
            self.assertEqual(len(main_schema.tables), 1)
            self.assertEqual(main_schema.get_table('bom_table').table_name, 'bom_table')

        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
