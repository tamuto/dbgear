import unittest
from dbgear.models.procedure import Procedure, ProcedureParameter, ProcedureManager


class TestProcedure(unittest.TestCase):

    def test_procedure_creation(self):
        """Test basic procedure creation and properties"""
        params = [
            ProcedureParameter(
                parameter_name="user_id",
                parameter_type="IN",
                data_type="INT"
            ),
            ProcedureParameter(
                parameter_name="result",
                parameter_type="OUT",
                data_type="VARCHAR(255)"
            )
        ]

        procedure = Procedure(
            procedure_name="get_user_info",
            display_name="Get User Information",
            parameters=params,
            body="SELECT name INTO result FROM users WHERE id = user_id;",
            deterministic=True,
            reads_sql_data=True,
            modifies_sql_data=False
        )

        self.assertEqual(procedure.procedure_name, "get_user_info")
        self.assertEqual(procedure.display_name, "Get User Information")
        self.assertEqual(len(procedure.parameters), 2)
        self.assertFalse(procedure.is_function)
        self.assertTrue(procedure.deterministic)
        self.assertTrue(procedure.reads_sql_data)
        self.assertFalse(procedure.modifies_sql_data)
        self.assertEqual(procedure.security_type, "DEFINER")

    def test_function_creation(self):
        """Test function creation (procedure with return type)"""
        params = [
            ProcedureParameter(
                parameter_name="user_id",
                parameter_type="IN",
                data_type="INT"
            )
        ]

        function = Procedure(
            procedure_name="get_user_name",
            display_name="Get User Name Function",
            parameters=params,
            return_type="VARCHAR(255)",
            body="RETURN (SELECT name FROM users WHERE id = user_id);",
            deterministic=True
        )

        self.assertTrue(function.is_function)
        self.assertEqual(function.return_type, "VARCHAR(255)")

    def test_procedure_manager(self):
        """Test ProcedureManager operations"""
        procedure1 = Procedure(
            procedure_name="proc1",
            display_name="Procedure 1",
            body="SELECT 1;"
        )

        procedure2 = Procedure(
            procedure_name="proc2",
            display_name="Procedure 2",
            body="SELECT 2;"
        )

        # Test manager initialization and operations
        procedures_dict = {}
        manager = ProcedureManager(procedures_dict)

        # Test append
        manager.append(procedure1)
        manager.append(procedure2)

        self.assertEqual(len(manager), 2)
        self.assertIn("proc1", manager)
        self.assertIn("proc2", manager)

        # Test getitem
        self.assertEqual(manager["proc1"].display_name, "Procedure 1")

        # Test iteration
        procedure_names = [proc.procedure_name for proc in manager]
        self.assertIn("proc1", procedure_names)
        self.assertIn("proc2", procedure_names)

        # Test remove
        manager.remove("proc1")
        self.assertEqual(len(manager), 1)
        self.assertNotIn("proc1", manager)

        # Test error cases
        with self.assertRaises(ValueError):
            manager.append(procedure2)  # Already exists

        with self.assertRaises(KeyError):
            manager.remove("nonexistent")  # Doesn't exist

    def test_parameter_with_default(self):
        """Test procedure parameter with default value"""
        param = ProcedureParameter(
            parameter_name="limit_count",
            parameter_type="IN",
            data_type="INT",
            default_value="10"
        )

        procedure = Procedure(
            procedure_name="get_recent_users",
            display_name="Get Recent Users",
            parameters=[param],
            body="SELECT * FROM users ORDER BY created_at DESC LIMIT limit_count;",
            reads_sql_data=True
        )

        self.assertEqual(procedure.parameters[0].default_value, "10")


if __name__ == '__main__':
    unittest.main()
