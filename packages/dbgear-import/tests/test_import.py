"""
Tests for dbgear-import functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path

from dbgear_import.importer import import_schema, list_importers


class TestImporter(unittest.TestCase):
    """Test the generic importer functionality."""

    def test_list_importers(self):
        """Test that we can list available importers."""
        importers = list_importers()
        self.assertIsInstance(importers, list)
        self.assertIn('a5sql_mk2', importers)

    def test_import_schema_invalid_importer(self):
        """Test that invalid importer raises ImportError."""
        with self.assertRaises(ImportError):
            import_schema('nonexistent_importer', '.', 'test.file', {})


class TestA5SQLMk2Importer(unittest.TestCase):
    """Test A5:SQL Mk-2 importer functionality."""

    def setUp(self):
        """Set up test data."""
        self.test_a5er_content = """[Manager]
Ver=1.00

[Entity]
PName=users
LName=ユーザー
Page=MAIN
Field="id","id","INT","NOT NULL","1","",""
Field="name","name","VARCHAR(100)","NOT NULL","","",""
Field="email","email","VARCHAR(255)","NOT NULL","","",""

[Entity]
PName=posts
LName=投稿
Page=MAIN
Field="id","id","INT","NOT NULL","1","",""
Field="user_id","user_id","INT","NOT NULL","","",""
Field="title","title","VARCHAR(200)","NOT NULL","","",""
Field="content","content","TEXT","","","",""

[Relation]
Entity1=users
Entity2=posts
Fields1=id
Fields2=user_id

[Comment]
Comment=これはテストコメントです
Page=MAIN
"""

    def test_a5sql_mk2_import(self):
        """Test A5:SQL Mk-2 import functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test .a5er file
            test_file = Path(temp_dir) / 'test.a5er'
            test_file.write_text(self.test_a5er_content, encoding='utf-8')

            # Import schema
            mapping = {'MAIN': 'main'}
            schema_manager = import_schema('a5sql_mk2', temp_dir, 'test.a5er', mapping)

            # Verify imported schema
            self.assertIsNotNone(schema_manager)
            self.assertIn('main', schema_manager.schemas)
            
            main_schema = schema_manager['main']
            self.assertEqual(len(main_schema.tables.tables), 2)
            
            # Check users table
            self.assertIn('users', main_schema.tables.tables)
            users_table = main_schema.tables['users']
            self.assertEqual(users_table.display_name, 'ユーザー')
            self.assertEqual(len(users_table.columns.columns), 3)
            
            # Check posts table
            self.assertIn('posts', main_schema.tables.tables)
            posts_table = main_schema.tables['posts']
            self.assertEqual(posts_table.display_name, '投稿')
            self.assertEqual(len(posts_table.columns.columns), 4)
            
            # Check relation
            self.assertEqual(len(posts_table.relations.relations), 1)
            
            # Check schema-level notes
            self.assertTrue(len(main_schema.notes.notes) > 0)

    def test_a5sql_mk2_mapping(self):
        """Test schema mapping functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test .a5er file with multiple pages
            content = """[Manager]
Ver=1.00

[Entity]
PName=users
Page=MAIN
Field="id","id","INT","NOT NULL","1","",""

[Entity]
PName=test_data
Page=TEST
Field="id","id","INT","NOT NULL","1","",""
"""
            test_file = Path(temp_dir) / 'test.a5er'
            test_file.write_text(content, encoding='utf-8')

            # Import with custom mapping
            mapping = {'MAIN': 'production', 'TEST': 'testing'}
            schema_manager = import_schema('a5sql_mk2', temp_dir, 'test.a5er', mapping)

            # Verify mapping
            self.assertIn('production', schema_manager.schemas)
            self.assertIn('testing', schema_manager.schemas)
            self.assertNotIn('main', schema_manager.schemas)


if __name__ == '__main__':
    unittest.main()