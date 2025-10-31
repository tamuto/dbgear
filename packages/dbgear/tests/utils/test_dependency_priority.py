"""
Test dependency resolution with prioritization of explicit dependencies over FK dependencies
"""
import unittest
from unittest.mock import MagicMock
from dbgear.utils.dependency import DependencyResolver
from dbgear.models.datamodel import DataModel
from dbgear.models.schema import Schema
from dbgear.models.table import Table
from dbgear.models.relation import Relation, EntityInfo


class TestDependencyPriority(unittest.TestCase):
    """Test cases for dependency resolution priority"""

    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyResolver()

    def _create_datamodel(self, table_name, dependencies=None):
        """Helper to create a DataModel with required fields"""
        return DataModel(
            folder="test_folder",
            environ="test_env",
            map_name="test_map",
            schema_name="test",
            table_name=table_name,
            description="Test table",
            sync_mode="replace",
            data_type="yaml",
            dependencies=dependencies or []
        )

    def test_explicit_dependencies_only_no_cycle(self):
        """Test explicit dependencies only without cycles"""
        # Create test data models
        dm1 = self._create_datamodel("table1")
        dm2 = self._create_datamodel("table2", dependencies=["test@table1"])
        dm3 = self._create_datamodel("table3", dependencies=["test@table2"])

        # Create schema without FK relations
        schema = Schema(name="test_schema")
        schema.tables_ = {
            "table1": Table(table_name="table1", display_name="table1", relations_=[]),
            "table2": Table(table_name="table2", display_name="table2", relations_=[]),
            "table3": Table(table_name="table3", display_name="table3", relations_=[])
        }

        # Resolve order
        result = self.resolver.resolve_insertion_order([dm1, dm2, dm3], schema)

        # Check order: table1 -> table2 -> table3
        result_keys = [f"{dm.schema_name}@{dm.table_name}" for dm in result]
        self.assertEqual(result_keys, ["test@table1", "test@table2", "test@table3"])

    def test_explicit_dependencies_with_cycle_should_error(self):
        """Test explicit dependencies with cycle should raise error"""
        # Create circular dependencies: table1 -> table2 -> table3 -> table1
        dm1 = self._create_datamodel("table1", dependencies=["test@table3"])
        dm2 = self._create_datamodel("table2", dependencies=["test@table1"])
        dm3 = self._create_datamodel("table3", dependencies=["test@table2"])

        # Create schema
        schema = Schema(name="test_schema")
        schema.tables_ = {
            "table1": Table(table_name="table1", display_name="table1", relations_=[]),
            "table2": Table(table_name="table2", display_name="table2", relations_=[]),
            "table3": Table(table_name="table3", display_name="table3", relations_=[])
        }

        # Should raise ValueError due to cycle
        with self.assertRaises(ValueError) as context:
            self.resolver.resolve_insertion_order([dm1, dm2, dm3], schema)

        self.assertIn("Circular dependency detected in explicit dependencies", str(context.exception))

    def test_fk_dependencies_only_no_cycle(self):
        """Test FK dependencies only without cycles"""
        # Create data models without explicit dependencies
        dm1 = self._create_datamodel("table1")
        dm2 = self._create_datamodel("table2")
        dm3 = self._create_datamodel("table3")

        # Create schema with FK relations: table2 -> table1, table3 -> table2
        schema = Schema(name="test_schema")
        schema.tables_ = {
            "table1": Table(table_name="table1", display_name="table1", relations_=[]),
            "table2": Table(
                table_name="table2",
                display_name="table2",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table1"),
                        bind_columns=[]
                    )
                ]
            ),
            "table3": Table(
                table_name="table3",
                display_name="table3",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table2"),
                        bind_columns=[]
                    )
                ]
            )
        }

        # Resolve order
        result = self.resolver.resolve_insertion_order([dm1, dm2, dm3], schema)

        # Check order: table1 -> table2 -> table3
        result_keys = [f"{dm.schema_name}@{dm.table_name}" for dm in result]
        self.assertEqual(result_keys, ["test@table1", "test@table2", "test@table3"])

    def test_fk_dependencies_with_cycle_should_ignore_fk(self):
        """Test FK dependencies with cycle should ignore FK causing cycle"""
        # Create data models without explicit dependencies
        dm1 = self._create_datamodel("table1")
        dm2 = self._create_datamodel("table2")
        dm3 = self._create_datamodel("table3")

        # Create schema with circular FK: table1 -> table2 -> table3 -> table1
        schema = Schema(name="test_schema")
        schema.tables_ = {
            "table1": Table(
                table_name="table1",
                display_name="table1",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table3"),
                        bind_columns=[]
                    )
                ]
            ),
            "table2": Table(
                table_name="table2",
                display_name="table2",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table1"),
                        bind_columns=[]
                    )
                ]
            ),
            "table3": Table(
                table_name="table3",
                display_name="table3",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table2"),
                        bind_columns=[]
                    )
                ]
            )
        }

        # Should NOT raise error, but should ignore FKs causing cycles
        result = self.resolver.resolve_insertion_order([dm1, dm2, dm3], schema)

        # Should return some valid order (exact order may vary depending on which FK is ignored)
        self.assertEqual(len(result), 3)
        result_keys = [f"{dm.schema_name}@{dm.table_name}" for dm in result]
        self.assertIn("test@table1", result_keys)
        self.assertIn("test@table2", result_keys)
        self.assertIn("test@table3", result_keys)

    def test_explicit_dependencies_override_fk(self):
        """Test explicit dependencies take priority over FK dependencies"""
        # Explicit: table1 -> table2
        # FK: table2 -> table1 (opposite direction)
        dm1 = self._create_datamodel("table1", dependencies=["test@table2"])
        dm2 = self._create_datamodel("table2")

        # FK says table2 depends on table1, but explicit says table1 depends on table2
        schema = Schema(name="test_schema")
        schema.tables_ = {
            "table1": Table(table_name="table1", display_name="table1", relations_=[]),
            "table2": Table(
                table_name="table2",
                display_name="table2",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table1"),
                        bind_columns=[]
                    )
                ]
            )
        }

        # Resolve order
        result = self.resolver.resolve_insertion_order([dm1, dm2], schema)

        # Explicit dependency should win: table2 -> table1
        result_keys = [f"{dm.schema_name}@{dm.table_name}" for dm in result]
        self.assertEqual(result_keys, ["test@table2", "test@table1"])

    def test_mixed_dependencies_fk_ignored_when_causing_cycle(self):
        """Test mixed dependencies where FK causing cycle is ignored"""
        # Explicit: table1 -> table2 -> table3
        # FK: table3 -> table1 (would cause cycle)
        dm1 = self._create_datamodel("table1")
        dm2 = self._create_datamodel("table2", dependencies=["test@table1"])
        dm3 = self._create_datamodel("table3", dependencies=["test@table2"])

        # FK from table3 to table1 would create cycle
        schema = Schema(name="test_schema")
        schema.tables_ = {
            "table1": Table(table_name="table1", display_name="table1", relations_=[]),
            "table2": Table(table_name="table2", display_name="table2", relations_=[]),
            "table3": Table(
                table_name="table3",
                display_name="table3",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table1"),
                        bind_columns=[]
                    )
                ]
            )
        }

        # Should NOT raise error, FK causing cycle should be ignored
        result = self.resolver.resolve_insertion_order([dm1, dm2, dm3], schema)

        # Check order based on explicit dependencies: table1 -> table2 -> table3
        result_keys = [f"{dm.schema_name}@{dm.table_name}" for dm in result]
        self.assertEqual(result_keys, ["test@table1", "test@table2", "test@table3"])

    def test_complex_scenario_with_multiple_fks_and_explicit(self):
        """Test complex scenario with multiple FKs and explicit dependencies"""
        # Explicit: table1 -> table3
        # FK: table2 -> table1, table3 -> table2, table4 -> table3
        # This creates: table1 -> table3 (explicit) and table1 -> table2 -> table3 (FK)
        # FK table3 -> table2 would conflict with explicit table1 -> table3
        dm1 = self._create_datamodel("table1")
        dm2 = self._create_datamodel("table2")
        dm3 = self._create_datamodel("table3", dependencies=["test@table1"])
        dm4 = self._create_datamodel("table4")

        schema = Schema(name="test_schema")
        schema.tables_ = {
            "table1": Table(table_name="table1", display_name="table1", relations_=[]),
            "table2": Table(
                table_name="table2",
                display_name="table2",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table1"),
                        bind_columns=[]
                    )
                ]
            ),
            "table3": Table(
                table_name="table3",
                display_name="table3",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table2"),
                        bind_columns=[]
                    )
                ]
            ),
            "table4": Table(
                table_name="table4",
                display_name="table4",
                relations_=[
                    Relation(
                        target=EntityInfo(schema_name="test", table_name="table3"),
                        bind_columns=[]
                    )
                ]
            )
        }

        # Should resolve without error
        result = self.resolver.resolve_insertion_order([dm1, dm2, dm3, dm4], schema)

        # Check that table1 comes before table3 (explicit dependency)
        result_keys = [f"{dm.schema_name}@{dm.table_name}" for dm in result]
        table1_idx = result_keys.index("test@table1")
        table3_idx = result_keys.index("test@table3")
        self.assertLess(table1_idx, table3_idx, "table1 should come before table3")

        # Check that table3 comes before table4 (FK dependency, should be kept if no cycle)
        table4_idx = result_keys.index("test@table4")
        self.assertLess(table3_idx, table4_idx, "table3 should come before table4")


if __name__ == '__main__':
    unittest.main()
