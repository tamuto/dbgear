#!/usr/bin/env python3
"""
依存関係解決機能のテスト用サンプル

このスクリプトは、DependencyResolverの動作を確認するためのサンプルです。
実際のDBGearプロジェクトでの利用例を示しています。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/dbgear'))

from dbgear.models.datamodel import DataModel, DataParams
from dbgear.models.schema import Schema, SchemaManager
from dbgear.models.table import Table, TableManager
from dbgear.models.relation import Relation, RelationManager, EntityInfo, BindColumn
from dbgear.utils.dependency import DependencyResolver


def create_test_schema():
    """テスト用のスキーマを作成"""
    # テーブル定義
    roles_table = Table(
        table_name="roles",
        display_name="ロール",
        columns_=[],
        relations_=[]
    )
    
    users_table = Table(
        table_name="users", 
        display_name="ユーザー",
        columns_=[],
        relations_=[
            Relation(
                target=EntityInfo(schema_name="main", table_name="roles"),
                bind_columns=[BindColumn(source_column="role_id", target_column="id")]
            )
        ]
    )
    
    categories_table = Table(
        table_name="categories",
        display_name="カテゴリ",
        columns_=[],
        relations_=[]
    )
    
    products_table = Table(
        table_name="products",
        display_name="商品",
        columns_=[],
        relations_=[
            Relation(
                target=EntityInfo(schema_name="main", table_name="categories"),
                bind_columns=[BindColumn(source_column="category_id", target_column="id")]
            )
        ]
    )
    
    orders_table = Table(
        table_name="orders",
        display_name="注文",
        columns_=[],
        relations_=[
            Relation(
                target=EntityInfo(schema_name="main", table_name="users"),
                bind_columns=[BindColumn(source_column="user_id", target_column="id")]
            ),
            Relation(
                target=EntityInfo(schema_name="main", table_name="products"),
                bind_columns=[BindColumn(source_column="product_id", target_column="id")]
            )
        ]
    )
    
    tables = {
        "roles": roles_table,
        "users": users_table,
        "categories": categories_table,
        "products": products_table,
        "orders": orders_table
    }
    
    schema = Schema(name="main", tables_=tables)
    return schema


def create_test_datamodels():
    """テスト用のDataModelリストを作成"""
    datamodels = [
        DataModel(
            folder="/test",
            environ="development", 
            map_name="main",
            schema_name="main",
            table_name="orders",
            description="注文データ",
            sync_mode="drop_create",
            data_type="yaml",
            dependencies=[]  # FK依存のみ（users, products）
        ),
        DataModel(
            folder="/test",
            environ="development",
            map_name="main", 
            schema_name="main",
            table_name="users",
            description="ユーザーデータ",
            sync_mode="drop_create",
            data_type="yaml",
            dependencies=[]  # FK依存のみ（roles）
        ),
        DataModel(
            folder="/test",
            environ="development",
            map_name="main",
            schema_name="main", 
            table_name="products",
            description="商品データ",
            sync_mode="drop_create",
            data_type="yaml",
            dependencies=["main@categories"]  # 明示的依存関係
        ),
        DataModel(
            folder="/test",
            environ="development",
            map_name="main",
            schema_name="main",
            table_name="roles", 
            description="ロールデータ",
            sync_mode="drop_create",
            data_type="yaml",
            dependencies=[]  # 依存なし
        ),
        DataModel(
            folder="/test",
            environ="development",
            map_name="main",
            schema_name="main",
            table_name="categories",
            description="カテゴリデータ", 
            sync_mode="drop_create",
            data_type="yaml",
            dependencies=[]  # 依存なし
        )
    ]
    return datamodels


def test_dependency_resolution():
    """依存関係解決のテスト"""
    print("=== 依存関係解決テスト ===")
    
    # テストデータ作成
    schema = create_test_schema()
    datamodels = create_test_datamodels()
    
    print("元の順序:")
    for dm in datamodels:
        print(f"  {dm.schema_name}@{dm.table_name}")
    
    # 依存関係解決
    resolver = DependencyResolver()
    
    # 妥当性チェック
    print("\n依存関係チェック:")
    warnings = resolver.validate_dependencies(datamodels, schema)
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")
    else:
        print("  依存関係に問題はありません")
    
    # 順序解決
    try:
        ordered_datamodels = resolver.resolve_insertion_order(datamodels, schema)
        print("\n解決後の順序:")
        for dm in ordered_datamodels:
            print(f"  {dm.schema_name}@{dm.table_name}")
            
        # 期待される順序の確認
        expected = ["roles", "categories", "users", "products", "orders"]
        actual = [dm.table_name for dm in ordered_datamodels]
        
        print(f"\n期待される順序: {expected}")
        print(f"実際の順序:     {actual}")
        
        # 依存関係が満たされているかチェック
        table_positions = {table: i for i, table in enumerate(actual)}
        success = True
        
        for dm in ordered_datamodels:
            current_pos = table_positions[dm.table_name]
            
            # FK依存関係チェック
            if dm.table_name in schema.tables:
                table = schema.tables[dm.table_name]
                for relation in table.relations:
                    dep_table = relation.target.table_name
                    if dep_table in table_positions:
                        dep_pos = table_positions[dep_table]
                        if dep_pos >= current_pos:
                            print(f"  ERROR: {dm.table_name}({current_pos}) should come after {dep_table}({dep_pos})")
                            success = False
            
            # 明示的依存関係チェック
            for dep in dm.dependencies:
                dep_table = dep.split('@')[1]
                if dep_table in table_positions:
                    dep_pos = table_positions[dep_table]
                    if dep_pos >= current_pos:
                        print(f"  ERROR: {dm.table_name}({current_pos}) should come after {dep_table}({dep_pos})")
                        success = False
        
        if success:
            print("✅ 依存関係が正しく解決されました！")
        else:
            print("❌ 依存関係の解決に問題があります")
            
    except Exception as e:
        print(f"❌ エラー: {e}")


def test_circular_dependency():
    """循環依存のテスト"""
    print("\n=== 循環依存テスト ===")
    
    # 循環依存を持つDataModelを作成
    circular_datamodels = [
        DataModel(
            folder="/test",
            environ="development",
            map_name="main",
            schema_name="main",
            table_name="table_a",
            description="テーブルA",
            sync_mode="drop_create", 
            data_type="yaml",
            dependencies=["main@table_b"]
        ),
        DataModel(
            folder="/test",
            environ="development",
            map_name="main",
            schema_name="main",
            table_name="table_b",
            description="テーブルB",
            sync_mode="drop_create",
            data_type="yaml", 
            dependencies=["main@table_a"]
        )
    ]
    
    # 空のスキーマ
    empty_schema = Schema(name="main", tables_={})
    
    resolver = DependencyResolver()
    try:
        ordered = resolver.resolve_insertion_order(circular_datamodels, empty_schema)
        print("❌ 循環依存が検出されませんでした")
    except ValueError as e:
        print(f"✅ 循環依存が正しく検出されました: {e}")


if __name__ == "__main__":
    test_dependency_resolution()
    test_circular_dependency()