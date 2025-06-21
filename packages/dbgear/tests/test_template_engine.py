"""Unit tests for SQL template engine functionality."""

import unittest
from dbgear.core.models.schema import (
    Table, Column, ColumnType, Index, View, 
    MySQLTableOptions, Relation, EntityInfo, BindColumn, Note
)
from dbgear.core.dbio.templates.mysql import template_engine


class TestTemplateEngine(unittest.TestCase):
    """Test SQL template engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Basic column type
        self.varchar_type = ColumnType(
            column_type='VARCHAR',
            base_type='VARCHAR',
            length=100
        )
        
        # Numeric column type
        self.bigint_type = ColumnType(
            column_type='BIGINT',
            base_type='BIGINT'
        )
        
        # Decimal column type
        self.decimal_type = ColumnType(
            column_type='DECIMAL',
            base_type='DECIMAL',
            precision=10,
            scale=2
        )
        
        # Basic column
        self.basic_column = Column(
            column_name='name',
            display_name='Name',
            column_type=self.varchar_type,
            nullable=False
        )
        
        # Primary key column
        self.pk_column = Column(
            column_name='id',
            display_name='ID',
            column_type=self.bigint_type,
            nullable=False,
            primary_key=1,
            auto_increment=True
        )
        
        # Basic table
        self.basic_table = Table(
            instance='test',
            table_name='users',
            display_name='Users',
            columns=[self.pk_column, self.basic_column]
        )
    
    def test_basic_table_creation(self):
        """Test basic table creation template renders successfully."""
        sql = template_engine.render(
            'mysql_create_table',
            env='testdb',
            table=self.basic_table
        )
        
        # Assert that rendering succeeded (no exceptions)
        self.assertIsInstance(sql, str)
        self.assertTrue(len(sql) > 0)
        
        # Print for manual verification
        print("\n=== Basic Table Creation ===")
        print(sql)
        
        # Basic structure checks
        self.assertIn('CREATE TABLE', sql)
        self.assertIn('testdb.users', sql)
        self.assertIn('`id`', sql)
        self.assertIn('`name`', sql)
        self.assertIn('PRIMARY KEY', sql)
    
    def test_table_with_mysql_options(self):
        """Test table creation with MySQL-specific options."""
        mysql_options = MySQLTableOptions(
            engine='InnoDB',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            auto_increment=1000,
            row_format='DYNAMIC'
        )
        
        table = Table(
            instance='test',
            table_name='products',
            display_name='Products',
            columns=[self.pk_column],
            mysql_options=mysql_options
        )
        
        sql = template_engine.render(
            'mysql_create_table',
            env='testdb',
            table=table
        )
        
        self.assertIsInstance(sql, str)
        self.assertTrue(len(sql) > 0)
        
        print("\n=== Table with MySQL Options ===")
        print(sql)
        
        # Check MySQL options
        self.assertIn('ENGINE=InnoDB', sql)
        self.assertIn('DEFAULT CHARSET=utf8mb4', sql)
        self.assertIn('COLLATE=utf8mb4_unicode_ci', sql)
        self.assertIn('AUTO_INCREMENT=1000', sql)
        self.assertIn('ROW_FORMAT=DYNAMIC', sql)
    
    def test_table_with_foreign_keys(self):
        """Test table creation with foreign key constraints."""
        # Create a column that references another table
        category_id_column = Column(
            column_name='category_id',
            display_name='Category ID',
            column_type=self.bigint_type,
            nullable=True
        )
        
        # Create foreign key relation
        target_entity = EntityInfo(schema='testdb', table_name='categories')
        bind_column = BindColumn(source_column='category_id', target_column='id')
        relation = Relation(
            target=target_entity,
            bind_columns=[bind_column],
            constraint_name='fk_user_category',
            on_delete='CASCADE',
            on_update='RESTRICT'
        )
        
        table = Table(
            instance='test',
            table_name='users',
            display_name='Users',
            columns=[self.pk_column, self.basic_column, category_id_column],
            relations=[relation]
        )
        
        sql = template_engine.render(
            'mysql_create_table',
            env='testdb',
            table=table
        )
        
        self.assertIsInstance(sql, str)
        self.assertTrue(len(sql) > 0)
        
        print("\n=== Table with Foreign Keys ===")
        print(sql)
        
        # Check foreign key constraint
        self.assertIn('CONSTRAINT fk_user_category', sql)
        self.assertIn('FOREIGN KEY', sql)
        self.assertIn('REFERENCES categories', sql)
        self.assertIn('ON DELETE CASCADE', sql)
    
    def test_column_with_advanced_features(self):
        """Test columns with advanced MySQL features."""
        # Column with charset and collation
        text_column = Column(
            column_name='description',
            display_name='Description',
            column_type=ColumnType(column_type='TEXT', base_type='TEXT'),
            nullable=True,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        # Generated column
        computed_column = Column(
            column_name='full_name',
            display_name='Full Name',
            column_type=ColumnType(column_type='VARCHAR', base_type='VARCHAR', length=200),
            nullable=True,
            expression="CONCAT(first_name, ' ', last_name)",
            stored=True
        )
        
        # Column with notes
        note = Note(title="Important", content="This is a test column")
        noted_column = Column(
            column_name='status',
            display_name='Status',
            column_type=ColumnType(column_type='VARCHAR', base_type='VARCHAR', length=50),
            nullable=False,
            notes=[note]
        )
        
        table = Table(
            instance='test',
            table_name='advanced_test',
            display_name='Advanced Test',
            columns=[self.pk_column, text_column, computed_column, noted_column]
        )
        
        sql = template_engine.render(
            'mysql_create_table',
            env='testdb',
            table=table
        )
        
        self.assertIsInstance(sql, str)
        self.assertTrue(len(sql) > 0)
        
        print("\n=== Advanced Column Features ===")
        print(sql)
        
        # Check advanced features
        self.assertIn('CHARACTER SET utf8mb4', sql)
        self.assertIn('COLLATE utf8mb4_unicode_ci', sql)
        self.assertIn('GENERATED ALWAYS AS', sql)
        self.assertIn('STORED', sql)
        self.assertIn('COMMENT', sql)
    
    def test_index_creation(self):
        """Test index creation template."""
        # Basic index
        basic_index = Index(
            index_name='idx_name',
            columns=['name']
        )
        
        # Unique index
        unique_index = Index(
            index_name='idx_email_unique',
            columns=['email'],
            unique=True
        )
        
        # Multi-column index
        multi_index = Index(
            index_name='idx_name_status',
            columns=['name', 'status']
        )
        
        table = Table(
            instance='test',
            table_name='test_indexes',
            display_name='Test Indexes',
            columns=[self.pk_column, self.basic_column],
            indexes=[basic_index, unique_index, multi_index]
        )
        
        # Test each index
        for idx, index in enumerate([basic_index, unique_index, multi_index]):
            loop_context = type('LoopContext', (), {'index0': idx})()
            sql = template_engine.render(
                'mysql_create_index',
                env='testdb',
                table=table,
                index=index,
                loop=loop_context
            )
            
            self.assertIsInstance(sql, str)
            self.assertTrue(len(sql) > 0)
            
            print(f"\n=== Index Creation {idx + 1} ===")
            print(sql)
            
            # Basic checks
            self.assertIn('CREATE', sql)
            self.assertIn('INDEX', sql)
            self.assertIn(f'testdb.{table.table_name}', sql)
            
            if index.unique:
                self.assertIn('UNIQUE', sql)
    
    def test_view_creation(self):
        """Test view creation template."""
        view = View(
            instance='test',
            view_name='user_summary',
            display_name='User Summary',
            select_statement="""
            SELECT u.id, u.name, COUNT(o.id) as order_count
            FROM users u 
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name
            """.strip()
        )
        
        sql = template_engine.render(
            'mysql_create_view',
            env='testdb',
            view=view
        )
        
        self.assertIsInstance(sql, str)
        self.assertTrue(len(sql) > 0)
        
        print("\n=== View Creation ===")
        print(sql)
        
        # Basic checks
        self.assertIn('CREATE VIEW', sql)
        self.assertIn('testdb.user_summary', sql)
        self.assertIn('SELECT', sql)
        self.assertIn('FROM users', sql)
    
    def test_view_operations(self):
        """Test view utility operations (check existence, drop, create or replace, etc.)."""
        # Test CHECK VIEW EXISTS
        check_sql = template_engine.render('mysql_check_view_exists')
        
        self.assertIsInstance(check_sql, str)
        self.assertTrue(len(check_sql) > 0)
        
        print("\n=== Check View Exists ===")
        print(check_sql)
        
        self.assertIn('SELECT TABLE_NAME', check_sql)
        self.assertIn('information_schema.views', check_sql)
        self.assertIn('table_schema = :env', check_sql)
        self.assertIn('table_name = :view_name', check_sql)
        
        # Test DROP VIEW
        drop_sql = template_engine.render(
            'mysql_drop_view',
            env='testdb',
            view_name='old_view'
        )
        
        self.assertIsInstance(drop_sql, str)
        self.assertTrue(len(drop_sql) > 0)
        
        print("\n=== Drop View ===")
        print(drop_sql)
        
        self.assertIn('DROP VIEW IF EXISTS testdb.old_view', drop_sql)
        
        # Test CREATE OR REPLACE VIEW
        create_or_replace_sql = template_engine.render(
            'mysql_create_or_replace_view',
            env='production',
            view_name='stats_view',
            view_select_statement='SELECT COUNT(*) as total FROM users'
        )
        
        self.assertIsInstance(create_or_replace_sql, str)
        self.assertTrue(len(create_or_replace_sql) > 0)
        
        print("\n=== Create or Replace View ===")
        print(create_or_replace_sql)
        
        self.assertIn('CREATE OR REPLACE VIEW production.stats_view', create_or_replace_sql)
        self.assertIn('SELECT COUNT(*) as total FROM users', create_or_replace_sql)
        
        # Test GET VIEW DEFINITION
        get_definition_sql = template_engine.render('mysql_get_view_definition')
        
        self.assertIsInstance(get_definition_sql, str)
        self.assertTrue(len(get_definition_sql) > 0)
        
        print("\n=== Get View Definition ===")
        print(get_definition_sql)
        
        self.assertIn('SELECT VIEW_DEFINITION', get_definition_sql)
        self.assertIn('information_schema.views', get_definition_sql)
        
        # Test DEPENDENCY CHECKS
        check_table_dependency_sql = template_engine.render('mysql_check_dependency_exists')
        
        self.assertIsInstance(check_table_dependency_sql, str)
        self.assertTrue(len(check_table_dependency_sql) > 0)
        
        print("\n=== Check Table Dependency ===")
        print(check_table_dependency_sql)
        
        self.assertIn('information_schema.tables', check_table_dependency_sql)
        self.assertIn('dependency_name', check_table_dependency_sql)
        
        check_view_dependency_sql = template_engine.render('mysql_check_view_dependency_exists')
        
        self.assertIsInstance(check_view_dependency_sql, str)
        self.assertTrue(len(check_view_dependency_sql) > 0)
        
        print("\n=== Check View Dependency ===")
        print(check_view_dependency_sql)
        
        self.assertIn('information_schema.views', check_view_dependency_sql)
        self.assertIn('dependency_name', check_view_dependency_sql)
    
    def test_database_operations(self):
        """Test database creation and deletion templates."""
        # Test CREATE DATABASE
        create_sql = template_engine.render(
            'mysql_create_database',
            database_name='test_project',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        self.assertIsInstance(create_sql, str)
        self.assertTrue(len(create_sql) > 0)
        
        print("\n=== Database Creation ===")
        print(create_sql)
        
        self.assertIn('CREATE DATABASE test_project', create_sql)
        self.assertIn('CHARACTER SET utf8mb4', create_sql)
        self.assertIn('COLLATE utf8mb4_unicode_ci', create_sql)
        
        # Test DROP DATABASE
        drop_sql = template_engine.render(
            'mysql_drop_database',
            database_name='test_project'
        )
        
        self.assertIsInstance(drop_sql, str)
        self.assertTrue(len(drop_sql) > 0)
        
        print("\n=== Database Deletion ===")
        print(drop_sql)
        
        self.assertIn('DROP DATABASE test_project', drop_sql)
        
        # Test minimal CREATE DATABASE
        minimal_sql = template_engine.render(
            'mysql_create_database',
            database_name='minimal_db'
        )
        
        self.assertIsInstance(minimal_sql, str)
        self.assertTrue(len(minimal_sql) > 0)
        
        print("\n=== Minimal Database Creation ===")
        print(minimal_sql)
        
        self.assertIn('CREATE DATABASE minimal_db', minimal_sql)
        
        # Test CHECK DATABASE EXISTS
        check_db_sql = template_engine.render('mysql_check_database_exists')
        
        self.assertIsInstance(check_db_sql, str)
        self.assertTrue(len(check_db_sql) > 0)
        
        print("\n=== Check Database Exists ===")
        print(check_db_sql)
        
        self.assertIn('SHOW DATABASES LIKE', check_db_sql)
        self.assertIn(':database_name', check_db_sql)
    
    def test_table_operations(self):
        """Test table utility operations (check existence, drop)."""
        # Test CHECK TABLE EXISTS
        check_sql = template_engine.render('mysql_check_table_exists')
        
        self.assertIsInstance(check_sql, str)
        self.assertTrue(len(check_sql) > 0)
        
        print("\n=== Check Table Exists ===")
        print(check_sql)
        
        self.assertIn('SELECT TABLE_NAME', check_sql)
        self.assertIn('information_schema.tables', check_sql)
        self.assertIn('table_schema = :env', check_sql)
        self.assertIn('table_name = :table_name', check_sql)
        
        # Test DROP TABLE
        drop_sql = template_engine.render(
            'mysql_drop_table',
            env='testdb',
            table_name='old_table'
        )
        
        self.assertIsInstance(drop_sql, str)
        self.assertTrue(len(drop_sql) > 0)
        
        print("\n=== Drop Table ===")
        print(drop_sql)
        
        self.assertIn('DROP TABLE testdb.old_table', drop_sql)
    
    def test_data_operations(self):
        """Test data manipulation operations (insert, backup, restore)."""
        # Test INSERT INTO
        insert_sql = template_engine.render(
            'mysql_insert_into',
            env='testdb',
            table_name='users',
            column_names=['name', 'email', 'age'],
            value_placeholders=[':name', ':email', ':age']
        )
        
        self.assertIsInstance(insert_sql, str)
        self.assertTrue(len(insert_sql) > 0)
        
        print("\n=== Insert Into ===")
        print(insert_sql)
        
        self.assertIn('INSERT INTO testdb.users', insert_sql)
        self.assertIn('(`name`, `email`, `age`)', insert_sql)
        self.assertIn('VALUES (:name, :email, :age)', insert_sql)
        
        # Test BACKUP TABLE
        backup_sql = template_engine.render(
            'mysql_backup_table',
            env='production',
            table_name='orders',
            ymd='20240621'
        )
        
        self.assertIsInstance(backup_sql, str)
        self.assertTrue(len(backup_sql) > 0)
        
        print("\n=== Backup Table ===")
        print(backup_sql)
        
        self.assertIn('CREATE TABLE production.bak_orders_20240621', backup_sql)
        self.assertIn('SELECT * FROM production.orders', backup_sql)
        
        # Test RESTORE TABLE
        restore_sql = template_engine.render(
            'mysql_restore_table',
            env='production',
            table_name='orders',
            ymd='20240621'
        )
        
        self.assertIsInstance(restore_sql, str)
        self.assertTrue(len(restore_sql) > 0)
        
        print("\n=== Restore Table ===")
        print(restore_sql)
        
        self.assertIn('INSERT IGNORE INTO production.orders', restore_sql)
        self.assertIn('SELECT * FROM production.bak_orders_20240621', restore_sql)
        
        # Test CHECK BACKUP EXISTS
        check_backup_sql = template_engine.render('mysql_check_backup_exists')
        
        self.assertIsInstance(check_backup_sql, str)
        self.assertTrue(len(check_backup_sql) > 0)
        
        print("\n=== Check Backup Exists ===")
        print(check_backup_sql)
        
        self.assertIn('SELECT TABLE_NAME', check_backup_sql)
        self.assertIn('information_schema.tables', check_backup_sql)
        self.assertIn('table_name = :backup_table_name', check_backup_sql)
    
    def test_template_engine_error_handling(self):
        """Test template engine error handling."""
        # Test with missing template
        with self.assertRaises(Exception):
            template_engine.render('nonexistent_template')
        
        # Test with missing required parameters
        with self.assertRaises(Exception):
            template_engine.render('mysql_create_table')  # Missing env and table
    
    def test_complex_scenario(self):
        """Test a complex scenario with all features combined."""
        # Create a complex table with all features
        columns = [
            # Primary key with auto increment
            Column(
                column_name='id',
                display_name='ID',
                column_type=ColumnType(column_type='BIGINT', base_type='BIGINT'),
                nullable=False,
                primary_key=1,
                auto_increment=True
            ),
            # Text column with charset
            Column(
                column_name='title',
                display_name='Title',
                column_type=ColumnType(column_type='VARCHAR', base_type='VARCHAR', length=255),
                nullable=False,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            ),
            # Decimal column
            Column(
                column_name='price',
                display_name='Price',
                column_type=ColumnType(column_type='DECIMAL', base_type='DECIMAL', precision=10, scale=2),
                nullable=True,
                default_value='0.00'
            ),
            # Generated column
            Column(
                column_name='slug',
                display_name='Slug',
                column_type=ColumnType(column_type='VARCHAR', base_type='VARCHAR', length=255),
                nullable=True,
                expression="LOWER(REPLACE(title, ' ', '-'))",
                stored=False  # VIRTUAL
            ),
            # Foreign key column
            Column(
                column_name='category_id',
                display_name='Category ID',
                column_type=ColumnType(column_type='BIGINT', base_type='BIGINT'),
                nullable=True
            )
        ]
        
        # Indexes
        indexes = [
            Index(index_name='idx_title', columns=['title'], unique=True),
            Index(index_name='idx_price', columns=['price']),
            Index(index_name='idx_category_price', columns=['category_id', 'price'])
        ]
        
        # Foreign key relation
        relation = Relation(
            target=EntityInfo(schema='testdb', table_name='categories'),
            bind_columns=[BindColumn(source_column='category_id', target_column='id')],
            constraint_name='fk_product_category',
            on_delete='SET NULL',
            on_update='CASCADE'
        )
        
        # MySQL options
        mysql_options = MySQLTableOptions(
            engine='InnoDB',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            auto_increment=10000,
            row_format='DYNAMIC'
        )
        
        table = Table(
            instance='test',
            table_name='products',
            display_name='Products',
            columns=columns,
            indexes=indexes,
            relations=[relation],
            mysql_options=mysql_options
        )
        
        sql = template_engine.render(
            'mysql_create_table',
            env='production',
            table=table
        )
        
        self.assertIsInstance(sql, str)
        self.assertTrue(len(sql) > 0)
        
        print("\n=== Complex Scenario - Complete Table ===")
        print(sql)
        
        # Comprehensive checks
        self.assertIn('CREATE TABLE production.products', sql)
        self.assertIn('BIGINT NOT NULL AUTO_INCREMENT', sql)
        self.assertIn('VARCHAR(255)', sql)
        self.assertIn('DECIMAL(10, 2)', sql)
        self.assertIn('GENERATED ALWAYS AS', sql)
        self.assertIn('VIRTUAL', sql)
        self.assertIn('CHARACTER SET utf8mb4', sql)
        self.assertIn('COLLATE utf8mb4_unicode_ci', sql)
        self.assertIn('PRIMARY KEY', sql)
        self.assertIn('CONSTRAINT fk_product_category', sql)
        self.assertIn('FOREIGN KEY', sql)
        self.assertIn('ON DELETE SET NULL', sql)
        self.assertIn('ON UPDATE CASCADE', sql)
        self.assertIn('ENGINE=InnoDB', sql)
        self.assertIn('AUTO_INCREMENT=10000', sql)
        self.assertIn('ROW_FORMAT=DYNAMIC', sql)


if __name__ == '__main__':
    unittest.main(verbosity=2)