# Dependencies Management Specification

## 概要

DBGearコアライブラリに含まれるテーブル依存関係分析機能の仕様書です。指定されたテーブルに関連する依存関係を階層的に分析し、テーブルが参照するオブジェクト（右側）とテーブルを参照するオブジェクト（左側）を、指定された階層レベルまで取得できます。

## モジュール構成

### メインクラス

- `TableDependencyAnalyzer`: テーブル依存関係の分析を行うメインクラス
- `DependencyItem`: 個別の依存関係アイテムを表現するクラス

### ファイル場所
```
packages/dbgear/dbgear/misc/dependencies.py
```

## 使用方法

### 基本的な使用例

```python
from dbgear.models.schema import SchemaManager
from dbgear.misc.dependencies import TableDependencyAnalyzer

# スキーママネージャーの初期化
schema_manager = SchemaManager()
schema_manager.load('path/to/schema.yaml')

# 依存関係アナライザーの初期化
analyzer = TableDependencyAnalyzer(schema_manager, project_folder='path/to/project')

# 依存関係の分析（デフォルト: 両側3階層まで）
dependencies = analyzer.analyze('main', 'users')

# カスタム階層レベルでの分析
dependencies = analyzer.analyze(
    schema_name='main',
    table_name='users',
    left_level=2,   # 左側（参照元）2階層まで
    right_level=1   # 右側（参照先）1階層まで
)
```

## パラメータ仕様

### TableDependencyAnalyzer.analyze()

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|---|------|------------|------|
| schema_name | str | ✓ | - | スキーマ名 |
| table_name | str | ✓ | - | テーブル名 |
| left_level | int | - | 3 | 左側（参照元）の階層レベル (0-3) |
| right_level | int | - | 3 | 右側（参照先）の階層レベル (0-3) |

## 関係性の定義

### 右側（Right）- table_nameが参照するもの

1. **外部キー参照先テーブル** (`relation`)
   - relationのtargetで指定されるテーブル
   - bind_columnsで結びつくカラム情報

2. **インデックス** (`index`)
   - テーブルに定義されているインデックス
   - columnsで指定されるカラム情報

3. **初期データ** (`data`)
   - DataSourceで管理される初期データファイル
   - schema_name, table_nameで関連付け

### 左側（Left）- table_nameを参照するもの

1. **外部キー参照元テーブル** (`relation`)
   - 他テーブルから当テーブルへの外部キー参照
   - relationのtargetが当テーブルを指すもの

2. **ビュー** (`view`)
   - 当テーブルを参照するビュー
   - select_statementまたは_dependenciesで関連付け

3. **トリガー** (`trigger`)
   - 当テーブルに定義されているトリガー
   - table_nameで関連付け

## 戻り値形式

### データ構造

```python
{
    "target_table": {
        "schema_name": "main",
        "table_name": "users"
    },
    "left": {
        "level_1": [
            {
                "type": "relation",
                "schema_name": "main",
                "table_name": "orders",
                "object_name": "fk_orders_user_id",
                "details": {
                    "constraint_name": "fk_orders_user_id",
                    "bind_columns": [
                        {
                            "source_column": "user_id",
                            "target_column": "id"
                        }
                    ],
                    "on_delete": "CASCADE",
                    "on_update": "RESTRICT"
                }
            }
        ],
        "level_2": [...],
        "level_3": [...]
    },
    "right": {
        "level_1": [
            {
                "type": "relation",
                "schema_name": "main", 
                "table_name": "user_profiles",
                "object_name": "fk_users_profile_id",
                "details": {
                    "constraint_name": "fk_users_profile_id",
                    "bind_columns": [
                        {
                            "source_column": "profile_id",
                            "target_column": "id"
                        }
                    ],
                    "on_delete": "SET NULL",
                    "on_update": "RESTRICT"
                }
            }
        ],
        "level_2": [...],
        "level_3": [...]
    }
}
```

### DependencyItem.to_dict()出力形式

#### 共通フィールド

- `type`: オブジェクトタイプ (`relation`, `view`, `trigger`, `index`, `data`)
- `schema_name`: スキーマ名
- `table_name`: テーブル名（viewの場合はnull）
- `object_name`: オブジェクト名（制約名、ビュー名、トリガー名、インデックス名、データファイル名）
- `details`: タイプ固有の詳細情報
- `path`: level_2以上の場合、経路情報（どのオブジェクトを経由してきたか）

#### タイプ別詳細情報

**relation**
```python
{
    "constraint_name": "制約名",
    "bind_columns": [{"source_column": "元カラム", "target_column": "先カラム"}],
    "on_delete": "CASCADE|SET NULL|RESTRICT|NO ACTION",
    "on_update": "CASCADE|SET NULL|RESTRICT|NO ACTION",
    "cardinarity_source": "1|0..1|0..*|1..*",
    "cardinarity_target": "1|0..1|0..*|1..*"
}
```

**view**
```python
{
    "select_statement": "SELECT文",
    "referenced_columns": ["参照されるカラム一覧"],
    "dependencies": ["依存テーブル/ビュー一覧"]
}
```

**trigger**
```python
{
    "timing": "BEFORE|AFTER|INSTEAD OF",
    "event": "INSERT|UPDATE|DELETE",
    "condition": "WHEN条件",
    "body": "トリガー本体"
}
```

**index**
```python
{
    "columns": ["対象カラム一覧"],
    "index_type": "BTREE|HASH|FULLTEXT|SPATIAL",
    "unique": True|False,
    "partial_condition": "部分インデックス条件"
}
```

**data**
```python
{
    "environ": "環境名",
    "segment": "セグメント名", 
    "record_count": "レコード数",
    "data_file_path": "データファイルパス"
}
```

## 例外処理

### スキーマが存在しない場合
```python
ValueError: Schema 'invalid_schema' not found
```

### テーブルが存在しない場合  
```python
ValueError: Table 'invalid_table' not found in schema 'main'
```

### パラメータエラー
```python
ValueError: left_level must be between 0 and 3
ValueError: right_level must be between 0 and 3
```

## 階層レベルの解釈

### Level 0
- 依存関係を取得しない

### Level 1（直接参照）
- テーブルから直接参照される、またはテーブルを直接参照するオブジェクト

### Level 2（間接参照1階層）
- Level 1のオブジェクトから更に参照される、またはLevel 1のオブジェクトを参照するオブジェクト

### Level 3（間接参照2階層）
- Level 2のオブジェクトから更に参照される、またはLevel 2のオブジェクトを参照するオブジェクト

例：users → orders → order_items の場合
- usersから見て、ordersはlevel_1（left側）
- usersから見て、order_itemsはlevel_2（left側）

## 統合機能

このcore機能は、以下のDBGear機能と統合されています：

### DependencyResolver（utils/dependency.py）
- データ挿入時の依存関係解決
- 循環依存の検出
- トポロジカルソートによる挿入順序最適化

### Web Editor
- テーブル詳細ページでの依存関係表示
- Dependencies可視化機能
- ER図生成時の関係性情報提供

### 使用例

```python
# Web Editorでの使用例
from dbgear.misc.dependencies import TableDependencyAnalyzer

def get_table_dependencies(schema_manager, schema_name, table_name):
    analyzer = TableDependencyAnalyzer(schema_manager)
    return analyzer.analyze(schema_name, table_name, left_level=2, right_level=2)

# データ挿入順序の最適化での使用例  
from dbgear.utils.dependency import DependencyResolver

def optimize_insertion_order(datamodels, schema):
    resolver = DependencyResolver()
    return resolver.resolve_insertion_order(datamodels, schema)
```