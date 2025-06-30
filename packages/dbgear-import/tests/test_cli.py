"""
Tests for dbgear-import CLI functionality.
"""

import unittest
import tempfile
import sys
from io import StringIO
from pathlib import Path

from dbgear_import.main import create_parser, handle_schema_import, handle_list_importers


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        self.assertIsNotNone(parser)

    def test_list_importers_command(self):
        """Test list importers command."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            # Mock args object
            class MockArgs:
                pass
            
            args = MockArgs()
            result = handle_list_importers(args)
            
            # Check return code
            self.assertEqual(result, 0)
            
            # Check output
            output = captured_output.getvalue()
            self.assertIn('a5sql_mk2', output)
            
        finally:
            sys.stdout = old_stdout

    def test_schema_import_file_not_found(self):
        """Test schema import with non-existent file."""
        # Mock args object
        class MockArgs:
            importer_type = 'a5sql_mk2'
            source_file = '/nonexistent/file.a5er'
            output = 'test_output.yaml'
            mapping = None

        args = MockArgs()
        result = handle_schema_import(args)
        
        # Should return error code
        self.assertEqual(result, 1)

    def test_schema_import_success(self):
        """Test successful schema import."""
        test_content = """[Manager]
Ver=1.00

[Entity]
PName=test_table
Page=MAIN
Field="id","id","INT","NOT NULL","1","",""
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test .a5er file
            test_file = Path(temp_dir) / 'test.a5er'
            test_file.write_text(test_content, encoding='utf-8')
            
            # Create output file path
            output_file = Path(temp_dir) / 'output.yaml'
            
            # Mock args object
            class MockArgs:
                importer_type = 'a5sql_mk2'
                source_file = str(test_file)
                output = str(output_file)
                mapping = 'MAIN:main'

            args = MockArgs()
            result = handle_schema_import(args)
            
            # Should succeed
            self.assertEqual(result, 0)
            
            # Output file should be created
            self.assertTrue(output_file.exists())


if __name__ == '__main__':
    unittest.main()