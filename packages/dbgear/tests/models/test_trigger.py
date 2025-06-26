import unittest
import tempfile
import os
import yaml

from dbgear.models.trigger import Trigger, TriggerManager
from dbgear.models.schema import SchemaManager, Schema
from dbgear.models.notes import Note


class TestTrigger(unittest.TestCase):
    """Test Trigger and TriggerManager model operations"""

    def setUp(self):
        """Create temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.schema_yaml_path = os.path.join(self.temp_dir, 'schema.yaml')

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_trigger_model_creation(self):
        """Test Trigger model basic properties and creation"""
        # Create a trigger with all properties
        trigger = Trigger(
            instance='main',
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

        # Test basic properties
        self.assertEqual(trigger.instance, 'main')
        self.assertEqual(trigger.trigger_name, 'audit_trigger')
        self.assertEqual(trigger.display_name, 'Audit Trigger')
        self.assertEqual(trigger.table_name, 'users')
        self.assertEqual(trigger.timing, 'AFTER')
        self.assertEqual(trigger.event, 'INSERT')
        self.assertEqual(trigger.condition, 'NEW.status = "active"')
        self.assertIn('INSERT INTO audit_log', trigger.body)

        # Test notes property
        self.assertIsInstance(trigger.notes, object)  # NoteManager
        self.assertEqual(len(trigger.notes), 0)

    def test_trigger_model_with_notes(self):
        """Test Trigger model with notes"""
        # Create notes
        note1 = Note(title="Important", content="This trigger audits user insertions")
        note2 = Note(title="Performance", content="Consider indexing audit_log table")

        # Create trigger with notes
        trigger = Trigger(
            instance='main',
            trigger_name='audit_trigger',
            display_name='Audit Trigger',
            table_name='users',
            timing='AFTER',
            event='INSERT',
            body='INSERT INTO audit_log VALUES (NEW.id, NOW());',
            notes=[note1, note2]
        )

        # Test notes access
        self.assertEqual(len(trigger.notes), 2)
        self.assertEqual(trigger.notes_[0].title, "Important")
        self.assertEqual(trigger.notes_[0].content, "This trigger audits user insertions")
        self.assertEqual(trigger.notes_[1].title, "Performance")

    def test_trigger_model_simple(self):
        """Test simple Trigger model without optional fields"""
        # Create minimal trigger
        trigger = Trigger(
            instance='main',
            trigger_name='update_timestamp',
            display_name='Update Timestamp',
            table_name='products',
            timing='BEFORE',
            event='UPDATE',
            body='SET NEW.updated_at = NOW();'
        )

        # Test properties
        self.assertEqual(trigger.trigger_name, 'update_timestamp')
        self.assertEqual(trigger.table_name, 'products')
        self.assertEqual(trigger.timing, 'BEFORE')
        self.assertEqual(trigger.event, 'UPDATE')
        self.assertIsNone(trigger.condition)  # No condition
        self.assertEqual(trigger.body, 'SET NEW.updated_at = NOW();')

    def test_trigger_manager_crud_operations(self):
        """Test TriggerManager CRUD operations"""
        # Create triggers
        trigger1 = Trigger(
            instance='main',
            trigger_name='audit_trigger',
            display_name='Audit Trigger',
            table_name='users',
            timing='AFTER',
            event='INSERT',
            body='INSERT INTO audit_log VALUES (NEW.id);'
        )

        trigger2 = Trigger(
            instance='main',
            trigger_name='update_trigger',
            display_name='Update Trigger',
            table_name='users',
            timing='BEFORE',
            event='UPDATE',
            body='SET NEW.updated_at = NOW();'
        )

        # Test TriggerManager creation and add
        triggers_dict = {}
        trigger_manager = TriggerManager(triggers_dict)

        # Test initial state
        self.assertEqual(len(trigger_manager), 0)
        self.assertNotIn('audit_trigger', trigger_manager)

        # Test add operation
        trigger_manager.add(trigger1)
        self.assertEqual(len(trigger_manager), 1)
        self.assertIn('audit_trigger', trigger_manager)

        trigger_manager.add(trigger2)
        self.assertEqual(len(trigger_manager), 2)
        self.assertIn('update_trigger', trigger_manager)

        # Test __getitem__
        retrieved_trigger = trigger_manager['audit_trigger']
        self.assertEqual(retrieved_trigger.display_name, 'Audit Trigger')
        self.assertEqual(retrieved_trigger.table_name, 'users')

        # Test iteration
        trigger_names = [trigger.trigger_name for trigger in trigger_manager]
        self.assertIn('audit_trigger', trigger_names)
        self.assertIn('update_trigger', trigger_names)

        # Test remove operation
        trigger_manager.remove('audit_trigger')
        self.assertEqual(len(trigger_manager), 1)
        self.assertNotIn('audit_trigger', trigger_manager)
        self.assertIn('update_trigger', trigger_manager)

    def test_trigger_manager_exceptions(self):
        """Test TriggerManager exception handling"""
        trigger = Trigger(
            instance='main',
            trigger_name='test_trigger',
            display_name='Test Trigger',
            table_name='test_table',
            timing='AFTER',
            event='INSERT',
            body='SELECT 1;'
        )

        triggers_dict = {}
        trigger_manager = TriggerManager(triggers_dict)

        # Test add duplicate trigger
        trigger_manager.add(trigger)
        with self.assertRaises(ValueError) as context:
            trigger_manager.add(trigger)
        self.assertIn("already exists", str(context.exception))

        # Test remove non-existent trigger
        with self.assertRaises(KeyError) as context:
            trigger_manager.remove('non_existent_trigger')
        self.assertIn("does not exist", str(context.exception))

        # Test get non-existent trigger
        with self.assertRaises(KeyError):
            trigger_manager['non_existent_trigger']

    def test_trigger_manager_iteration(self):
        """Test TriggerManager iteration methods"""
        # Create test triggers
        triggers = [
            Trigger(
                instance='main',
                trigger_name=f'trigger_{i}',
                display_name=f'Trigger {i}',
                table_name='test_table',
                timing='AFTER',
                event='INSERT',
                body=f'SELECT {i};'
            )
            for i in range(3)
        ]

        # Setup manager
        triggers_dict = {}
        trigger_manager = TriggerManager(triggers_dict)
        for trigger in triggers:
            trigger_manager.add(trigger)

        # Test __len__
        self.assertEqual(len(trigger_manager), 3)

        # Test __iter__
        iterated_triggers = list(trigger_manager)
        self.assertEqual(len(iterated_triggers), 3)

        # Test __contains__
        self.assertIn('trigger_0', trigger_manager)
        self.assertIn('trigger_1', trigger_manager)
        self.assertIn('trigger_2', trigger_manager)
        self.assertNotIn('trigger_3', trigger_manager)

    def test_schema_trigger_integration(self):
        """Test Schema integration with triggers"""
        # Create schema with triggers
        schema_manager = SchemaManager()
        main_schema = Schema(name='main')
        schema_manager.schemas['main'] = main_schema

        # Create triggers
        audit_trigger = Trigger(
            instance='main',
            trigger_name='audit_trigger',
            display_name='Audit Trigger',
            table_name='users',
            timing='AFTER',
            event='INSERT',
            body='INSERT INTO audit_log VALUES (NEW.id, NOW());'
        )

        update_trigger = Trigger(
            instance='main',
            trigger_name='update_trigger',
            display_name='Update Trigger',
            table_name='products',
            timing='BEFORE',
            event='UPDATE',
            body='SET NEW.updated_at = NOW();'
        )

        # Add triggers to schema
        main_schema.triggers.add(audit_trigger)
        main_schema.triggers.add(update_trigger)

        # Test schema trigger access
        self.assertEqual(len(main_schema.triggers), 2)
        self.assertIn('audit_trigger', main_schema.triggers)
        self.assertIn('update_trigger', main_schema.triggers)

        retrieved_trigger = main_schema.triggers['audit_trigger']
        self.assertEqual(retrieved_trigger.table_name, 'users')
        self.assertEqual(retrieved_trigger.timing, 'AFTER')

    def test_schema_trigger_yaml_roundtrip(self):
        """Test Schema with triggers YAML save/load roundtrip"""
        # Create schema with triggers
        schema_manager = SchemaManager()
        main_schema = Schema(name='main')
        schema_manager.schemas['main'] = main_schema

        # Create complex trigger with all features
        complex_trigger = Trigger(
            instance='main',
            trigger_name='complex_audit_trigger',
            display_name='Complex Audit Trigger',
            table_name='users',
            timing='AFTER',
            event='INSERT',
            condition='NEW.status = "active" AND NEW.role != "guest"',
            body="""
            INSERT INTO audit_log (
                table_name,
                action,
                user_id,
                timestamp,
                details
            ) VALUES (
                'users',
                'INSERT',
                NEW.id,
                NOW(),
                CONCAT('New user: ', NEW.name, ' with status: ', NEW.status)
            );
            """.strip(),
            notes=[
                Note(title="Purpose", content="Audits new active user registrations"),
                Note(title="Performance", content="Consider partitioning audit_log by date")
            ]
        )

        # Add trigger to schema
        main_schema.triggers.add(complex_trigger)

        # Test save
        schema_manager.save(self.schema_yaml_path)
        self.assertTrue(os.path.exists(self.schema_yaml_path))

        # Test load
        loaded_schema_manager = SchemaManager.load(self.schema_yaml_path)
        self.assertIn('main', loaded_schema_manager.schemas)

        loaded_schema = loaded_schema_manager['main']
        self.assertEqual(len(loaded_schema.triggers), 1)
        self.assertIn('complex_audit_trigger', loaded_schema.triggers)

        loaded_trigger = loaded_schema.triggers['complex_audit_trigger']
        self.assertEqual(loaded_trigger.display_name, 'Complex Audit Trigger')
        self.assertEqual(loaded_trigger.table_name, 'users')
        self.assertEqual(loaded_trigger.timing, 'AFTER')
        self.assertEqual(loaded_trigger.event, 'INSERT')
        self.assertIn('NEW.status = "active"', loaded_trigger.condition)
        self.assertIn('INSERT INTO audit_log', loaded_trigger.body)
        self.assertEqual(len(loaded_trigger.notes), 2)
        self.assertEqual(loaded_trigger.notes_[0].title, "Purpose")

    def test_trigger_yaml_load_from_existing_file(self):
        """Test loading Schema with triggers from existing YAML file"""
        # Create test schema data with triggers
        schema_data = {
            'schemas': {
                'main': {
                    'triggers': {
                        'user_audit': {
                            'displayName': 'User Audit Trigger',
                            'tableName': 'users',
                            'timing': 'AFTER',
                            'event': 'INSERT',
                            'condition': 'NEW.active = 1',
                            'body': 'INSERT INTO user_audit (user_id, action) VALUES (NEW.id, "INSERT");',
                            'notes': [
                                {
                                    'title': 'Security',
                                    'content': 'Tracks all user insertions for security audit'
                                }
                            ]
                        },
                        'product_update': {
                            'displayName': 'Product Update Trigger',
                            'tableName': 'products',
                            'timing': 'BEFORE',
                            'event': 'UPDATE',
                            'body': 'SET NEW.updated_at = NOW();'
                        }
                    }
                }
            }
        }

        # Write test data
        with open(self.schema_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(schema_data, f, allow_unicode=True)

        # Test load
        loaded_schema_manager = SchemaManager.load(self.schema_yaml_path)
        loaded_schema = loaded_schema_manager['main']

        # Verify triggers
        self.assertEqual(len(loaded_schema.triggers), 2)
        self.assertIn('user_audit', loaded_schema.triggers)
        self.assertIn('product_update', loaded_schema.triggers)

        # Test user_audit trigger
        user_audit = loaded_schema.triggers['user_audit']
        self.assertEqual(user_audit.display_name, 'User Audit Trigger')
        self.assertEqual(user_audit.table_name, 'users')
        self.assertEqual(user_audit.timing, 'AFTER')
        self.assertEqual(user_audit.event, 'INSERT')
        self.assertEqual(user_audit.condition, 'NEW.active = 1')
        self.assertIn('INSERT INTO user_audit', user_audit.body)
        self.assertEqual(len(user_audit.notes), 1)
        self.assertEqual(user_audit.notes_[0].title, 'Security')

        # Test product_update trigger
        product_update = loaded_schema.triggers['product_update']
        self.assertEqual(product_update.display_name, 'Product Update Trigger')
        self.assertEqual(product_update.table_name, 'products')
        self.assertEqual(product_update.timing, 'BEFORE')
        self.assertEqual(product_update.event, 'UPDATE')
        self.assertIsNone(product_update.condition)  # No condition
        self.assertEqual(product_update.body, 'SET NEW.updated_at = NOW();')


if __name__ == '__main__':
    unittest.main(verbosity=2)