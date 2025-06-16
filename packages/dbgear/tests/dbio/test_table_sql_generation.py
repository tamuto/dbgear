import unittest
from unittest.mock import MagicMock, patch

from dbgear.core.dbio.table import _column_sql, create, insert
from dbgear.core.models.schema import Table, Field, Index


class TestTableSQLGeneration(unittest.TestCase):

    def test_basic_column_sql(self):
        """Test basic column SQL generation."""
        field = Field(
            column_name="name",
            display_name="Name",
            column_type="VARCHAR(100)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )
        
        sql = _column_sql(field)
        expected = "`name` VARCHAR(100) NOT NULL"
        self.assertEqual(sql, expected)

    def test_auto_increment_column_sql(self):
        """Test AUTO_INCREMENT column SQL generation."""
        field = Field(
            column_name="id",
            display_name="ID",
            column_type="BIGINT",
            nullable=False,
            primary_key=1,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=True,
            charset=None,
            collation=None
        )
        
        sql = _column_sql(field)
        expected = "`id` BIGINT NOT NULL AUTO_INCREMENT"
        self.assertEqual(sql, expected)

    def test_charset_collation_column_sql(self):
        """Test character set and collation in column SQL."""
        field = Field(
            column_name="name",
            display_name="Name",
            column_type="VARCHAR(100)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=False,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )
        
        sql = _column_sql(field)
        expected = "`name` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL"
        self.assertEqual(sql, expected)

    def test_stored_expression_column_sql(self):
        """Test STORED generated column SQL generation."""
        field = Field(
            column_name="full_name",
            display_name="Full Name",
            column_type="VARCHAR(101)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression="CONCAT(last_name, ' ', first_name)",
            stored=True,
            auto_increment=False,
            charset=None,
            collation=None
        )
        
        sql = _column_sql(field)
        expected = "`full_name` VARCHAR(101) NOT NULL GENERATED ALWAYS AS (CONCAT(last_name, ' ', first_name)) STORED"
        self.assertEqual(sql, expected)

    def test_virtual_expression_column_sql(self):
        """Test VIRTUAL generated column SQL generation."""
        field = Field(
            column_name="email_domain",
            display_name="Email Domain",
            column_type="VARCHAR(255)",
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment=None,
            expression="SUBSTRING_INDEX(email, '@', -1)",
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )
        
        sql = _column_sql(field)
        expected = "`email_domain` VARCHAR(255) GENERATED ALWAYS AS (SUBSTRING_INDEX(email, '@', -1)) VIRTUAL"
        self.assertEqual(sql, expected)

    def test_column_with_comment_sql(self):
        """Test column with comment SQL generation."""
        field = Field(
            column_name="price",
            display_name="Price",
            column_type="DECIMAL(10,2)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment="Product price in USD",
            expression=None,
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )
        
        sql = _column_sql(field)
        expected = "`price` DECIMAL(10,2) NOT NULL COMMENT 'Product price in USD'"
        self.assertEqual(sql, expected)

    def test_column_with_comment_escaping(self):
        """Test column comment with single quote escaping."""
        field = Field(
            column_name="note",
            display_name="Note",
            column_type="TEXT",
            nullable=True,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment="User's note with 'quotes'",
            expression=None,
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )
        
        sql = _column_sql(field)
        expected = "`note` TEXT COMMENT 'User''s note with ''quotes'''"
        self.assertEqual(sql, expected)

    def test_default_value_column_sql(self):
        """Test column with default value SQL generation."""
        field = Field(
            column_name="created_at",
            display_name="Created At",
            column_type="TIMESTAMP",
            nullable=False,
            primary_key=None,
            default_value="CURRENT_TIMESTAMP",
            foreign_key=None,
            comment=None,
            expression=None,
            stored=False,
            auto_increment=False,
            charset=None,
            collation=None
        )
        
        sql = _column_sql(field)
        expected = "`created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        self.assertEqual(sql, expected)

    def test_complex_expression_column_sql(self):
        """Test complex expression column SQL generation."""
        field = Field(
            column_name="age_category",
            display_name="Age Category",
            column_type="VARCHAR(20)",
            nullable=False,
            primary_key=None,
            default_value=None,
            foreign_key=None,
            comment="Age classification",
            expression="CASE WHEN age < 20 THEN '未成年' WHEN age < 65 THEN '成人' ELSE '高齢者' END",
            stored=True,
            auto_increment=False,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )
        
        sql = _column_sql(field)
        expected = "`age_category` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL GENERATED ALWAYS AS (CASE WHEN age < 20 THEN '未成年' WHEN age < 65 THEN '成人' ELSE '高齢者' END) STORED COMMENT 'Age classification'"
        self.assertEqual(sql, expected)

    @patch('dbgear.core.dbio.table.engine')
    def test_create_table_with_expressions(self, mock_engine):
        """Test CREATE TABLE SQL generation with expression columns."""
        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
                    column_name="id",
                    display_name="ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=1,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=True,
                    charset=None,
                    collation=None
                ),
                Field(
                    column_name="first_name",
                    display_name="First Name",
                    column_type="VARCHAR(50)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=False,
                    charset="utf8mb4",
                    collation="utf8mb4_unicode_ci"
                ),
                Field(
                    column_name="last_name",
                    display_name="Last Name",
                    column_type="VARCHAR(50)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=False,
                    charset="utf8mb4",
                    collation="utf8mb4_unicode_ci"
                ),
                Field(
                    column_name="full_name",
                    display_name="Full Name",
                    column_type="VARCHAR(101)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression="CONCAT(last_name, ' ', first_name)",
                    stored=True,
                    auto_increment=False,
                    charset=None,
                    collation=None
                )
            ],
            indexes=[]
        )
        
        mock_conn = MagicMock()
        create(mock_conn, "testdb", table)
        
        # Verify that execute was called
        self.assertTrue(mock_engine.execute.called)
        
        # Get the actual SQL that was executed
        call_args = mock_engine.execute.call_args[0]
        actual_sql = call_args[1]
        
        # Verify the SQL contains expected elements
        self.assertIn("CREATE TABLE testdb.users", actual_sql)
        self.assertIn("AUTO_INCREMENT", actual_sql)
        self.assertIn("CHARACTER SET utf8mb4", actual_sql)
        self.assertIn("COLLATE utf8mb4_unicode_ci", actual_sql)
        self.assertIn("GENERATED ALWAYS AS (CONCAT(last_name, ' ', first_name)) STORED", actual_sql)
        self.assertIn("primary key (`id`)", actual_sql)

    @patch('dbgear.core.dbio.table.engine')
    def test_insert_excludes_generated_columns(self, mock_engine):
        """Test INSERT statement excludes generated columns."""
        table = Table(
            instance="test",
            table_name="users",
            display_name="Users",
            fields=[
                Field(
                    column_name="id",
                    display_name="ID",
                    column_type="BIGINT",
                    nullable=False,
                    primary_key=1,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=True,
                    charset=None,
                    collation=None
                ),
                Field(
                    column_name="first_name",
                    display_name="First Name",
                    column_type="VARCHAR(50)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression=None,
                    stored=False,
                    auto_increment=False,
                    charset=None,
                    collation=None
                ),
                Field(
                    column_name="full_name",
                    display_name="Full Name",
                    column_type="VARCHAR(101)",
                    nullable=False,
                    primary_key=None,
                    default_value=None,
                    foreign_key=None,
                    comment=None,
                    expression="CONCAT(last_name, ' ', first_name)",
                    stored=True,
                    auto_increment=False,
                    charset=None,
                    collation=None
                )
            ],
            indexes=[]
        )
        
        mock_conn = MagicMock()
        test_data = [{"first_name": "John"}]
        
        insert(mock_conn, "testdb", table, test_data)
        
        # Verify that execute was called
        self.assertTrue(mock_engine.execute.called)
        
        # Get the actual SQL that was executed
        call_args = mock_engine.execute.call_args[0]
        actual_sql = call_args[1]
        
        # Verify the SQL excludes generated column but includes other columns
        self.assertIn("INSERT INTO testdb.users", actual_sql)
        self.assertIn("`first_name`", actual_sql)
        self.assertNotIn("`full_name`", actual_sql)  # Generated column should be excluded


if __name__ == '__main__':
    unittest.main()