# schema.yaml 仕様書

## 概要

`schema.yaml`は、DBGearプロジェクトのデータベーススキーマ定義を管理するファイルです。テーブル、ビュー、トリガー、インデックス、リレーション、カラム型定義を包括的に管理し、DBGearの中核となるスキーマ情報を提供します。

## ファイル配置

`schema.yaml`はプロジェクトのルートディレクトリに配置します。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル（本ファイル）
├── development/          # 開発環境ディレクトリ
├── test/                 # テスト環境ディレクトリ
└── production/           # 本番環境ディレクトリ
```

## 基本構造

### 必須項目

```yaml
schemas:
  main:
    tables:
      table_name:
        # テーブル定義
    views:
      view_name:
        # ビュー定義
    triggers:
      trigger_name:
        # トリガー定義
```

### 項目詳細

#### schemas
- **型**: オブジェクト
- **必須**: はい
- **説明**: スキーマグループのコンテナ。通常は`main`スキーマを定義

#### tables
- **型**: オブジェクト
- **説明**: テーブル定義のコレクション
- **子要素**: 
  - `display_name`: テーブルの表示名
  - `fields`/`columns`: カラム定義のリスト
  - `indexes`: インデックス定義のリスト
  - `relations`: リレーション定義のリスト
  - `mysql_options`: MySQL固有オプション
  - `notes`: ノート情報のリスト

#### views
- **型**: オブジェクト
- **説明**: ビュー定義のコレクション
- **子要素**:
  - `display_name`: ビューの表示名
  - `select_statement`: SQL SELECT文
  - `comment`: コメント
  - `notes`: ノート情報のリスト

#### triggers
- **型**: オブジェクト
- **説明**: トリガー定義のコレクション
- **子要素**:
  - `display_name`: トリガーの表示名
  - `table_name`: 対象テーブル名
  - `timing`: 実行タイミング（BEFORE/AFTER/INSTEAD OF）
  - `event`: 実行イベント（INSERT/UPDATE/DELETE）
  - `condition`: WHEN条件式（オプション）
  - `body`: トリガー本体SQL
  - `notes`: ノート情報のリスト

#### columns（カラム定義）
- **型**: リスト
- **説明**: テーブルのカラム定義
- **重要**: 以前の`fields`は`columns`に名称変更されました
- **子要素**:
  - `column_name`: カラム名（必須）
  - `display_name`: 表示名（オプション）
  - `column_type`: カラム型（ColumnTypeオブジェクト、必須）
  - `nullable`: NULL許可フラグ（デフォルト: true）
  - `primary_key`: 主キー順序（1から開始、オプション）
  - `auto_increment`: 自動増分フラグ（デフォルト: false）
  - `default_value`: デフォルト値（オプション）
  - `expression`: 生成カラムの式（オプション）
  - `stored`: 生成カラムの保存フラグ（デフォルト: false）
  - `charset`: 文字セット（MySQL用、オプション）
  - `collation`: 照合順序（MySQL用、オプション）
  - `notes`: カラムレベルのノート（オプション）

#### indexes
- **型**: リスト
- **説明**: インデックス定義
- **子要素**:
  - `index_name`: インデックス名
  - `columns`: 対象カラムのリスト
  - `unique`: ユニーク制約フラグ
  - `index_type`: インデックス種別（BTREE、HASH等）

#### relations
- **型**: リスト
- **説明**: 外部キー制約定義
- **子要素**:
  - `target`: 参照先テーブル情報
  - `bind_columns`: カラムバインディング
  - `constraint_name`: 制約名
  - `on_delete`: DELETE時動作
  - `on_update`: UPDATE時動作

#### registry
- **型**: オブジェクト
- **説明**: カスタムカラム型定義レジストリ

#### notes
- **型**: リスト
- **説明**: ドキュメンテーション用ノート（全エンティティ共通）
- **重要**: ノート情報はドキュメント目的のみで、SQL生成時には含まれません
- **子要素**:  
  - `title`: タイトル（必須）
  - `content`: 内容（必須）
  - `checked`: 確認済みフラグ（デフォルト: false）

#### column_type（カラム型オブジェクト）
- **説明**: 構造化されたカラム型定義
- **子要素**:
  - `column_type`: 型の文字列表現（例: "VARCHAR(255)"）
  - `base_type`: 基本型名（例: "VARCHAR"）
  - `length`: 長さ（数値型・文字列型用）
  - `precision`: 精度（DECIMAL型用）
  - `scale`: スケール（DECIMAL型用）
  - `items`: ENUM/SET型の選択肢

## 設定例

### 基本的なテーブル定義

```yaml
schemas:
  main:
    tables:
      users:
        display_name: ユーザー
        columns:
          - column_name: id
            display_name: ID
            column_type:
              column_type: BIGINT
              base_type: BIGINT
            nullable: false
            primary_key: 1
            auto_increment: true
          - column_name: name
            display_name: 名前
            column_type:
              column_type: VARCHAR(100)
              base_type: VARCHAR
              length: 100
            nullable: false
          - column_name: email
            display_name: メールアドレス
            column_type:  
              column_type: VARCHAR(255)
              base_type: VARCHAR
              length: 255
            nullable: true
        indexes:
          - index_name: idx_users_email
            columns: [email]
            unique: true
        notes:
          - title: 設計方針
            content: ユーザー基本情報を管理するマスターテーブル
            checked: true
```

### カラム型レジストリの活用例

```yaml
schemas:
  main:
    registry:
      short_text:
        column_type: VARCHAR(100)
        base_type: VARCHAR
        length: 100
      long_text:
        column_type: TEXT
        base_type: TEXT
    tables:
      articles:
        display_name: 記事
        columns:
          - column_name: title  
            column_type: short_text  # レジストリ参照
          - column_name: content
            column_type: long_text   # レジストリ参照
```

### ビュー定義

```yaml
schemas:
  main:
    views:
      active_users:
        display_name: アクティブユーザー
        select_statement: |
          SELECT id, name, email
          FROM users
          WHERE email IS NOT NULL
```

### トリガー定義

```yaml
schemas:
  main:
    triggers:
      user_audit_trigger:
        display_name: ユーザー監査トリガー
        table_name: users
        timing: AFTER
        event: INSERT
        condition: 'NEW.status = "active"'
        body: |
          INSERT INTO audit_log (
              table_name, action, user_id, timestamp
          ) VALUES (
              'users', 'INSERT', NEW.id, NOW()
          );
        notes:
          - title: 目的
            content: アクティブユーザーの登録を監査
```

### JSON型カラムのデータ処理

DBGearでは、JSON型カラムに対してYAML形式での辞書データ入力をサポートしています。

#### JSONデータの定義方法

データファイル（`.dat`）内で、JSON型カラムに辞書形式でデータを定義すると、自動的にJSON文字列に変換されてINSERT文が実行されます。

```yaml
# データファイル例: main@test_table.dat
- col_id: '001'
  name: 'サンプル'
  json_column:
    ja: "こんにちは世界"
    en: "Hello World"
    settings:
      theme: "dark"
      language: "ja"
  created_at: NOW()
```

#### JSONカラムの変換処理

- YAMLファイル内の辞書オブジェクトは、INSERT時に自動的にJSON文字列に変換されます
- 変換処理は`dbgear.dbio.table._col_conv()`関数で実行されます
- 変換例：
  ```python
  # YAML辞書データ
  {"ja": "こんにちは", "en": "Hello"}
  
  # JSON文字列変換後
  '{"ja": "こんにちは", "en": "Hello"}'
  ```

#### 使用例

```yaml
schemas:
  main:
    tables:
      products:
        columns:
          - column_name: id
            column_type:
              column_type: BIGINT
              base_type: BIGINT
            nullable: false
            primary_key: 1
          - column_name: i18n_data
            column_type:
              column_type: JSON
              base_type: JSON
            nullable: true
```

```yaml
# データファイル: main@products.dat
- id: 1
  i18n_data:
    ja:
      name: "商品名"
      description: "商品説明"
    en:
      name: "Product Name"
      description: "Product Description"
    metadata:
      version: "1.0"
      tags: ["electronics", "smartphone"]
```

この機能により、多言語対応データや設定情報など、構造化されたデータを効率的に管理できます。

この仕様により、DBGearプロジェクトのスキーマ定義を統一的に管理できます。