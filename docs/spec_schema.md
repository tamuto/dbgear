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
- **子要素**:
  - `column_name`: カラム名
  - `display_name`: 表示名
  - `column_type`: カラム型（ColumnTypeオブジェクト）
  - `nullable`: NULL許可フラグ
  - `primary_key`: 主キー順序
  - `auto_increment`: 自動増分フラグ
  - `default_value`: デフォルト値
  - `expression`: 生成カラムの式
  - `stored`: 生成カラムの保存フラグ
  - `charset`: 文字セット
  - `collation`: 照合順序

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
- **説明**: ドキュメンテーション用ノート
- **子要素**:
  - `title`: タイトル
  - `content`: 内容
  - `checked`: 確認済みフラグ

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

この仕様により、DBGearプロジェクトのスキーマ定義を統一的に管理できます。