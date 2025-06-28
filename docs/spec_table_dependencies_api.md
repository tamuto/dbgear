# Table Dependencies API Specification

## 概要

指定されたテーブルに関連する依存関係を階層的に取得するAPIの仕様書です。テーブルが参照するオブジェクト（右側）とテーブルを参照するオブジェクト（左側）を、指定された階層レベルまで取得できます。

## API エンドポイント

```
GET /api/schemas/{schema_name}/tables/{table_name}/dependencies
```

## パラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|---|------|------------|------|
| schema_name | string | ✓ | - | スキーマ名 |
| table_name | string | ✓ | - | テーブル名 |
| left_level | integer | - | 3 | 左側（参照元）の階層レベル (1-3) |
| right_level | integer | - | 3 | 右側（参照先）の階層レベル (1-3) |

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

## レスポンス形式

### JSONデータ構造

```json
{
  "data": {
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
        },
        {
          "type": "view",
          "schema_name": "main",
          "table_name": null,
          "object_name": "user_summary_view",
          "details": {
            "select_statement": "SELECT u.id, u.name, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name",
            "referenced_columns": ["id", "name"]
          }
        },
        {
          "type": "trigger",
          "schema_name": "main",
          "table_name": "users",
          "object_name": "trg_users_audit",
          "details": {
            "timing": "AFTER",
            "event": "UPDATE",
            "condition": null,
            "body": "INSERT INTO user_audit_log ..."
          }
        }
      ],
      "level_2": [
        {
          "type": "relation",
          "schema_name": "main",
          "table_name": "order_items",
          "object_name": "fk_order_items_order_id",
          "details": {
            "constraint_name": "fk_order_items_order_id",
            "bind_columns": [
              {
                "source_column": "order_id",
                "target_column": "id"
              }
            ],
            "on_delete": "CASCADE",
            "on_update": "RESTRICT"
          },
          "path": [
            {
              "schema_name": "main",
              "table_name": "orders",
              "relation_type": "relation"
            }
          ]
        }
      ],
      "level_3": []
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
        },
        {
          "type": "index",
          "schema_name": "main",
          "table_name": "users",
          "object_name": "idx_users_email",
          "details": {
            "columns": ["email"],
            "index_type": "BTREE",
            "unique": true,
            "partial_condition": null
          }
        },
        {
          "type": "data",
          "schema_name": "main",
          "table_name": "users",
          "object_name": "main@users.dat",
          "details": {
            "environ": "development",
            "segment": null,
            "record_count": 10,
            "data_file_path": "development/test/main@users.dat"
          }
        }
      ],
      "level_2": [],
      "level_3": []
    }
  },
  "message": "Table dependencies retrieved successfully"
}
```

### データ構造の詳細

#### 共通フィールド

- `type`: オブジェクトタイプ (`relation`, `view`, `trigger`, `index`, `data`)
- `schema_name`: スキーマ名
- `table_name`: テーブル名（viewの場合はnull）
- `object_name`: オブジェクト名（制約名、ビュー名、トリガー名、インデックス名、データファイル名）
- `details`: タイプ固有の詳細情報
- `path`: level_2以上の場合、経路情報（どのオブジェクトを経由してきたか）

#### タイプ別詳細情報

**relation**
```json
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
```json
{
  "select_statement": "SELECT文",
  "referenced_columns": ["参照されるカラム一覧"],
  "dependencies": ["依存テーブル/ビュー一覧"]
}
```

**trigger**
```json
{
  "timing": "BEFORE|AFTER|INSTEAD OF",
  "event": "INSERT|UPDATE|DELETE",
  "condition": "WHEN条件",
  "body": "トリガー本体"
}
```

**index**
```json
{
  "columns": ["対象カラム一覧"],
  "index_type": "BTREE|HASH|FULLTEXT|SPATIAL",
  "unique": true|false,
  "partial_condition": "部分インデックス条件"
}
```

**data**
```json
{
  "environ": "環境名",
  "segment": "セグメント名",
  "record_count": "レコード数",
  "data_file_path": "データファイルパス"
}
```

## エラーレスポンス

### スキーマが存在しない場合
```json
{
  "error": "Schema 'invalid_schema' not found",
  "status_code": 404
}
```

### テーブルが存在しない場合
```json
{
  "error": "Table 'invalid_table' not found in schema 'main'",
  "status_code": 404
}
```

### パラメータエラー
```json
{
  "error": "Invalid level parameter. Level must be between 1 and 3",
  "status_code": 400
}
```

## 使用例

### 全ての依存関係を取得
```
GET /api/schemas/main/tables/users/dependencies
```

### 左側の直接参照のみを取得
```
GET /api/schemas/main/tables/users/dependencies?left_level=1&right_level=0
```

### 右側の2階層まで取得
```
GET /api/schemas/main/tables/users/dependencies?left_level=0&right_level=2
```

## 階層レベルの解釈

### Level 1（直接参照）
- テーブルから直接参照される、またはテーブルを直接参照するオブジェクト

### Level 2（間接参照1階層）
- Level 1のオブジェクトから更に参照される、またはLevel 1のオブジェクトを参照するオブジェクト

### Level 3（間接参照2階層）
- Level 2のオブジェクトから更に参照される、またはLevel 2のオブジェクトを参照するオブジェクト

例：users → orders → order_items の場合
- usersから見て、ordersはlevel_1（left側）
- usersから見て、order_itemsはlevel_2（left側）