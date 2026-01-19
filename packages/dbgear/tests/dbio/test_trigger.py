"""Unit tests for trigger operations."""

import unittest
from unittest.mock import Mock, patch

from dbgear.models.trigger import Trigger
from dbgear.dbio import trigger


class TestTriggerOperations(unittest.TestCase):
    """Test trigger CRUD operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_conn = Mock()
        self.env = 'testdb'

        # Sample trigger for testing
        self.test_trigger = Trigger(
            instance='test',
            trigger_name='audit_trigger',
            display_name='Audit Trigger',
            table_name='users',
            timing='AFTER',
            event='INSERT',
            condition='NEW.status = "active"',
            body="""
            INSERT INTO audit_log (table_name, action, user_id, timestamp)
            VALUES ('users', 'INSERT', NEW.id, NOW());
            """.strip()
        )

        # Simple trigger without condition
        self.simple_trigger = Trigger(
            instance='test',
            trigger_name='simple_trigger',
            display_name='Simple Trigger',
            table_name='products',
            timing='BEFORE',
            event='UPDATE',
            body='SET NEW.updated_at = NOW();'
        )

    @patch('dbgear.dbio.trigger.engine')
    @patch('dbgear.dbio.trigger.template_engine')
    def test_create_trigger(self, mock_template_engine, mock_engine):
        """Test trigger creation."""
        # Setup mocks
        expected_sql = "CREATE TRIGGER audit_trigger AFTER INSERT ON testdb.users FOR EACH ROW WHEN (NEW.status = \"active\") INSERT INTO audit_log..."
        mock_template_engine.render.return_value = expected_sql

        # Execute
        trigger.create(self.mock_conn, self.env, self.test_trigger)

        # Verify template rendering
        mock_template_engine.render.assert_called_once_with(
            'mysql_create_trigger',
            env=self.env,
            trigger=self.test_trigger
        )

        # Verify SQL execution
        mock_engine.execute.assert_called_once_with(
            self.mock_conn,
            expected_sql,
            dryrun=False
        )

    @patch('dbgear.dbio.trigger.engine')
    @patch('dbgear.dbio.trigger.template_engine')
    def test_create_simple_trigger(self, mock_template_engine, mock_engine):
        """Test simple trigger creation without condition."""
        # Setup mocks
        expected_sql = "CREATE TRIGGER simple_trigger BEFORE UPDATE ON testdb.products FOR EACH ROW SET NEW.updated_at = NOW();"
        mock_template_engine.render.return_value = expected_sql

        # Execute
        trigger.create(self.mock_conn, self.env, self.simple_trigger)

        # Verify template rendering
        mock_template_engine.render.assert_called_once_with(
            'mysql_create_trigger',
            env=self.env,
            trigger=self.simple_trigger
        )

        # Verify SQL execution
        mock_engine.execute.assert_called_once_with(
            self.mock_conn,
            expected_sql,
            dryrun=False
        )

    @patch('dbgear.dbio.trigger.engine')
    @patch('dbgear.dbio.trigger.template_engine')
    def test_drop_trigger(self, mock_template_engine, mock_engine):
        """Test trigger deletion."""
        # Setup mocks
        expected_sql = "DROP TRIGGER IF EXISTS testdb.audit_trigger"
        mock_template_engine.render.return_value = expected_sql

        # Execute
        trigger.drop(self.mock_conn, self.env, self.test_trigger)

        # Verify template rendering
        mock_template_engine.render.assert_called_once_with(
            'mysql_drop_trigger',
            env=self.env,
            trigger_name=self.test_trigger.trigger_name
        )

        # Verify SQL execution
        mock_engine.execute.assert_called_once_with(
            self.mock_conn,
            expected_sql,
            dryrun=False
        )

    @patch('dbgear.dbio.trigger.engine')
    @patch('dbgear.dbio.trigger.template_engine')
    def test_is_exist_true(self, mock_template_engine, mock_engine):
        """Test trigger existence check - trigger exists."""
        # Setup mocks
        expected_sql = "SELECT TRIGGER_NAME FROM information_schema.triggers WHERE trigger_schema = :env AND trigger_name = :trigger_name"
        mock_template_engine.render.return_value = expected_sql
        mock_engine.select_one.return_value = {'TRIGGER_NAME': 'audit_trigger'}

        # Execute
        result = trigger.is_exist(self.mock_conn, self.env, self.test_trigger)

        # Verify template rendering
        mock_template_engine.render.assert_called_once_with('mysql_check_trigger_exists')

        # Verify SQL execution
        mock_engine.select_one.assert_called_once_with(
            self.mock_conn,
            expected_sql,
            {'env': self.env, 'trigger_name': self.test_trigger.trigger_name}
        )

        # Verify result
        self.assertTrue(result)

    @patch('dbgear.dbio.trigger.engine')
    @patch('dbgear.dbio.trigger.template_engine')
    def test_is_exist_false(self, mock_template_engine, mock_engine):
        """Test trigger existence check - trigger does not exist."""
        # Setup mocks
        expected_sql = "SELECT TRIGGER_NAME FROM information_schema.triggers WHERE trigger_schema = :env AND trigger_name = :trigger_name"
        mock_template_engine.render.return_value = expected_sql
        mock_engine.select_one.return_value = None

        # Execute
        result = trigger.is_exist(self.mock_conn, self.env, self.test_trigger)

        # Verify template rendering
        mock_template_engine.render.assert_called_once_with('mysql_check_trigger_exists')

        # Verify SQL execution
        mock_engine.select_one.assert_called_once_with(
            self.mock_conn,
            expected_sql,
            {'env': self.env, 'trigger_name': self.test_trigger.trigger_name}
        )

        # Verify result
        self.assertFalse(result)

    @patch('dbgear.dbio.trigger.engine')
    @patch('dbgear.dbio.trigger.template_engine')
    def test_trigger_workflow(self, mock_template_engine, mock_engine):
        """Test complete trigger workflow: check existence, create, check again, drop."""
        # Setup mocks for different calls
        def mock_render_side_effect(template_name, **kwargs):
            if template_name == 'mysql_check_trigger_exists':
                return "SELECT TRIGGER_NAME FROM information_schema.triggers..."
            elif template_name == 'mysql_create_trigger':
                return "CREATE TRIGGER audit_trigger..."
            elif template_name == 'mysql_drop_trigger':
                return "DROP TRIGGER IF EXISTS testdb.audit_trigger"
            return ""

        mock_template_engine.render.side_effect = mock_render_side_effect

        # First check: trigger doesn't exist
        mock_engine.select_one.return_value = None
        exists_before = trigger.is_exist(self.mock_conn, self.env, self.test_trigger)
        self.assertFalse(exists_before)

        # Create trigger
        trigger.create(self.mock_conn, self.env, self.test_trigger)

        # Second check: trigger exists
        mock_engine.select_one.return_value = {'TRIGGER_NAME': 'audit_trigger'}
        exists_after = trigger.is_exist(self.mock_conn, self.env, self.test_trigger)
        self.assertTrue(exists_after)

        # Drop trigger
        trigger.drop(self.mock_conn, self.env, self.test_trigger)

        # Verify all calls were made
        self.assertEqual(mock_template_engine.render.call_count, 4)  # 2 checks + 1 create + 1 drop
        self.assertEqual(mock_engine.select_one.call_count, 2)  # 2 existence checks
        self.assertEqual(mock_engine.execute.call_count, 2)  # 1 create + 1 drop

    def test_trigger_model_properties(self):
        """Test trigger model properties are accessible."""
        # Test basic properties
        self.assertEqual(self.test_trigger.trigger_name, 'audit_trigger')
        self.assertEqual(self.test_trigger.display_name, 'Audit Trigger')
        self.assertEqual(self.test_trigger.table_name, 'users')
        self.assertEqual(self.test_trigger.timing, 'AFTER')
        self.assertEqual(self.test_trigger.event, 'INSERT')
        self.assertEqual(self.test_trigger.condition, 'NEW.status = "active"')
        self.assertIn('INSERT INTO audit_log', self.test_trigger.body)

        # Test simple trigger without condition
        self.assertEqual(self.simple_trigger.trigger_name, 'simple_trigger')
        self.assertEqual(self.simple_trigger.table_name, 'products')
        self.assertEqual(self.simple_trigger.timing, 'BEFORE')
        self.assertEqual(self.simple_trigger.event, 'UPDATE')
        self.assertIsNone(self.simple_trigger.condition)
        self.assertEqual(self.simple_trigger.body, 'SET NEW.updated_at = NOW();')


if __name__ == '__main__':
    unittest.main(verbosity=2)
