# DBGear

データベース初期データ管理のためのローカル開発ツールです。データベースのスキーマ定義と初期データをYAML形式で管理し、Web UIを通じて直感的にデータを編集できます。

## モノレポ構成

DBGearは3つの独立したパッケージで構成されています：

- **dbgear**: コアライブラリとCLIツール
- **dbgear-web**: Webインターフェース（FastAPI、APIエンドポイントは `/api` プレフィックス）
- **frontend**: 新しいReactフロントエンドパッケージ（Shadcn/UI + TanStack Router + RSBuild）
- **frontend.bak**: 旧フロントエンドパッケージ（Material-UI + React Router + Webpack）

## インストール

### CLI使用（コアライブラリ）
```bash
pip install dbgear
```

### Web UI使用
```bash
pip install dbgear-web  # 自動的にdbgearもインストールされます
```

### 開発用インストール
```bash
# リポジトリをクローン
git clone https://github.com/tamuto/dbgear.git
cd dbgear

# CLIパッケージの開発
cd packages/dbgear
poetry install

# Webパッケージの開発
cd packages/dbgear-web
poetry install

# 新しいフロントエンドパッケージの開発
cd packages/frontend
pnpm install
```

## 特徴

- **Web UI でのデータ編集**: 直感的なインターフェースでデータベースの初期データを編集
- **スキーマ連携**: テーブル定義に基づいたデータ入力支援と制約チェック
- **関連データ管理**: 外部キー参照の自動解決により、IDのコピペ作業が不要
- **ビュー管理**: データベースビューの定義と管理に対応
- **バージョン管理対応**: YAML形式でのデータ保存により、Gitでの差分管理が可能
- **複数環境対応**: 開発・テスト・本番など、環境ごとのデータ管理
- **プラグイン機構**: カスタムデータ変換やバインディングの拡張が可能
- **テスト連携**: ユニットテストでの利用を想定した設計

## クイックスタート

### 1. プロジェクトの作成

```bash
mkdir my-database-project
cd my-database-project
```

`project.yaml` を作成：

```yaml
project_name: MyProject
description: Database initial data management

definitions:
  - type: a5sql_mk2
    filename: ./schema.a5er
    mapping:
      MAIN: main

bindings:
  created_at:
    type: fixed
    value: NOW()
  user_id:
    type: fixed
    value: system

rules:
  created_at: created_at
  updated_at: created_at

deployments:
  localhost: mysql+pymysql://root:password@localhost/mydb?charset=utf8mb4
```

### 2. 環境の設定

```bash
mkdir development
```

`development/_mapping.yaml` を作成：

```yaml
id: mydb_dev
parent: null
instances:
  - main
```

### 3. CLI使用

```bash
# データベースへの適用
dbgear apply localhost development --all drop

# 差分のみ適用
dbgear apply localhost development --all delta

# 特定のテーブルのみ適用
dbgear apply localhost development --target users
```

### 4. Web UI使用

```bash
# Webサーバーの起動
dbgear-web --project . --port 5000

# オプション指定
dbgear-web --project ./my-project --host 0.0.0.0 --port 8080
```

ブラウザで http://localhost:5000 にアクセスして、Web UIでデータを編集します。

## プロジェクト設定

### definitions

データベーススキーマの定義方法を指定します。

#### A5:SQL Mk-2 形式
```yaml
definitions:
  - type: a5sql_mk2
    filename: ./schema.a5er
    mapping:
      MAIN: main
```

#### MySQL 直接接続
```yaml
definitions:
  - type: mysql
    connect: mysql+pymysql://user:pass@host/db?charset=utf8mb4
    mapping:
      schema_name: instance_name
```

#### DBGear ネイティブ形式
```yaml
definitions:
  - type: dbgear_schema
    filename: ./schema.yaml
    mapping:
      main: main
```

#### 選択リスト定義
```yaml
definitions:
  - type: selectable
    prefix: _select
    items:
      status: ステータス
      category: カテゴリ
```

## スキーマ定義

### DBGear ネイティブ形式

DBGearのネイティブYAML形式では、テーブル、ビュー、インデックス、リレーションを定義できます。

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
            charset: utf8mb4
            collation: utf8mb4_unicode_ci
        indexes:
          - index_name: idx_email
            columns: [email]
            unique: true
            index_type: BTREE
        relations:
          - target:
              schema: main
              table_name: departments
            bind_columns:
              - source_column: department_id
                target_column: id
            constraint_name: fk_user_department
            on_delete: CASCADE
            on_update: RESTRICT
        mysql_options:
          engine: InnoDB
          charset: utf8mb4
          collation: utf8mb4_unicode_ci
          auto_increment: 1000
        notes:
          - title: 設計メモ
            content: ユーザーマスターテーブル
            checked: false

    views:
      active_users:
        display_name: アクティブユーザー
        select_statement: |
          SELECT 
            id,
            name,
            email
          FROM users
          WHERE email IS NOT NULL
        notes:
          - title: 用途
            content: メールアドレスが設定されたユーザーのみを表示
            checked: true
```

### 最新のコアモデル仕様

DBGearは、Pydanticベースの型安全なデータモデルシステムを採用し、包括的なデータベーススキーマ管理を実現しています。

#### アーキテクチャの特徴
- **Pydanticベース**: すべてのモデルが`BaseSchema`を継承し、自動検証とJSON/YAMLシリアライゼーションを提供
- **Managerパターン**: 各エンティティコレクション（Schema、Table、Column、View、Index、Relation）は専用のManagerクラスで管理
- **統一されたCRUD操作**: `add()`, `remove()`, `__getitem__`, `__iter__`, `__contains__`による一貫したアクセス方法
- **型安全性**: TypeScriptライクな完全な型ヒントとランタイム検証

#### コアエンティティモデル

**Schema & SchemaManager**
- 複数スキーマの管理とYAML永続化
- 自動入力機能によるスキーマ/テーブル名の自動設定
- カラムタイプレジストリとグローバルノート管理

**Table & TableManager**
- 包括的なMySQLサポート（ストレージエンジン、パーティション、文字セット）
- `MySQLTableOptions`による高度なテーブル設定
- カラム、インデックス、リレーションの統合管理

**Column & ColumnManager**
- 構造化された`ColumnType`オブジェクトによる型管理
- MySQL固有機能：AUTO_INCREMENT、生成カラム（STORED/VIRTUAL）、文字セット・照合順序
- 名前とインデックス両方でのアクセス対応

**ColumnType & ColumnTypeRegistry**
- `parse_column_type()`による文字列からの自動解析
- MySQL全タイプサポート（VARCHAR、INT、DECIMAL、ENUM/SET、JSON等）
- 型チェック機能：`is_numeric_type()`, `is_string_type()`, `is_date_time_type()`
- カスタム型の登録・管理機能

**View & ViewManager**
- SQL文ベースのビュー定義
- 将来のSQL解析機能に対応した`ViewColumn`準備
- 依存関係自動検出の基盤

**Index & IndexManager**
- PostgreSQL機能を含む包括的なインデックス定義
- 部分インデックス、包含カラム、ストレージパラメータ対応
- 複数のインデックスタイプ（BTREE、HASH、FULLTEXT、SPATIAL）

**Relation & RelationManager**
- 物理制約と論理関係の統合管理
- 外部キー制約（ON DELETE/UPDATE動作、遅延制約）
- カーディナリティとUML関係タイプの表現

**Note & NoteManager**
- 全エンティティ統一のノートシステム
- レビュー追跡機能（`checked`フラグ）
- DB物理コメントとは独立した設計情報管理

#### データ管理・環境モデル

**DataModel & DataSource**
- Webインターフェース用のデータグリッドレイアウト設定
- テーブル、マトリックス、単一値の3つのレイアウト対応
- YAMLベースのデータファイル管理（セグメント化対応）

**Environ & Environment Management**
- 環境ごとのスキーマ・テナント・マッピング管理
- 遅延読み込みによる効率的なリソース管理

**Tenant & Multi-tenant Support**
- マルチテナント設定レジストリ
- データベース接続情報とプレフィックス管理

**Project Management**
- トップレベルプロジェクト設定
- 環境とスキーマの統合管理

#### 例外処理とエラーハンドリング
- 統一された例外階層（`DBGearError`基底クラス）
- エンティティ操作の安全性確保
- 制約違反の適切な通知

### bindings

データの自動設定ルールを定義します。

```yaml
bindings:
  # 固定値
  system_user:
    type: fixed
    value: SYSTEM
  
  # 現在時刻
  current_time:
    type: fixed
    value: NOW()
  
  # 関数呼び出し
  new_uuid:
    type: call
    value: uuid
  
  # プラグイン拡張
  custom_logic:
    type: extend
    value: my_plugin
```

### rules

フィールド名に基づいた自動バインディングルール。

```yaml
rules:
  created_by: system_user
  created_at: current_time
  updated_at: current_time
  .*_flag: y_or_n           # 正規表現使用可能
```

## データレイアウト

### Table レイアウト
通常のテーブル形式でのデータ編集。

```yaml
layout: table
description: ユーザーマスター
settings:
  user_id:
    type: new_uuid
  created_at:
    type: current_time
```

### Matrix レイアウト
マトリックス形式でのデータ編集（権限設定など）。

```yaml
layout: matrix
description: ユーザー権限マトリックス
```

### Single レイアウト
単一レコードのデータ編集（設定値など）。

```yaml
layout: single
description: システム設定
```

## CLIコマンド

### apply
データベースにデータを適用します。

```bash
# 基本構文
dbgear apply <deployment> <environment> [options]

# オプション
--target TABLE_NAME    # 特定のテーブルのみ適用
--all drop            # 全テーブルを削除して再作成
--all delta           # 差分のみ適用
```

## Webコマンド

### dbgear-web
Webサーバーを起動します。

```bash
# 基本構文
dbgear-web [options]

# オプション
--project PROJECT_DIR  # プロジェクトディレクトリ (デフォルト: database)
--port PORT            # ポート番号 (デフォルト: 5000)
--host HOST            # ホスト名 (デフォルト: 0.0.0.0)
```

## プラグイン開発

カスタムデータ変換ロジックをプラグインとして実装できます。

### プラグインの作成

```python
# my_plugin/__init__.py
def convert(project, mapping, instance, table, data_model, *args):
    """
    カスタムデータ変換処理
    
    Args:
        project: Projectオブジェクト（project.py）
        mapping: Mappingオブジェクト（mapping.py）
        instance: スキーマインスタンス名
        table: テーブル名
        data_model: DataModelオブジェクト（datamodel.py）
        *args: バインディング定義からの引数
    
    Returns:
        変換後の値
    """
    return f"custom_value_{args[0]}"
```

### プラグインの登録

```yaml
# project.yaml
bindings:
  my_custom:
    type: extend
    value: my_plugin
```

## 開発ワークフロー

### 1. テスト用データの準備
```bash
# テスト環境用のデータを作成
mkdir test
echo "id: test_db\ninstances:\n  - main" > test/_mapping.yaml
dbgear-web --project .
# Web UIでテストデータを編集
```

### 2. ユニットテストでの利用
```python
from dbgear.models.project import Project
from dbgear.models.environ import EnvironManager

def setUp(self):
    # 最新のモデルAPIを使用
    project = Project.load('./project')
    environ_manager = project.envs
    test_env = environ_manager['test']
    
    # スキーマとデータモデルにアクセス
    schemas = test_env.schemas
    data_models = test_env.data_models  # DataModelManagerアクセス
```

### 3. 本番データの準備
```bash
# 本番用データを作成
mkdir production
dbgear apply production_db production --all drop
```

## 開発環境セットアップ

### フロントエンド開発

```bash
# 新しいフロントエンドディレクトリに移動
cd packages/frontend

# 依存関係をインストール
pnpm install

# 開発サーバー起動（ポート8080）
pnpm run dev

# 本番用ビルド（../dbgear-web/dbgear_web/static/ に出力）
pnpm run build
```

#### 旧フロントエンド（frontend.bak）の開発

```bash
# 旧フロントエンドディレクトリに移動
cd packages/frontend.bak

# 依存関係をインストール
pnpm install

# 開発用ビルド
pnpm run build

# 本番用ビルド
pnpm run build:prod

# ウォッチモード
pnpm run watch

# 開発サーバー起動
pnpm run dev

# TypeScript型チェック
pnpm run type-check

# ESLint実行
pnpm run lint
```

### テスト実行

各パッケージでtaskipyを使用してテストを実行します：

```bash
# Core (CLI) パッケージのテスト
cd packages/dbgear
task test           # 全テスト実行
task test-fast      # 軽量テストのみ
task lint           # flake8によるコードチェック
task clean          # ビルド成果物のクリーンアップ

# Web パッケージのテスト
cd packages/dbgear-web
task test           # 全テスト実行
task test-fast      # 軽量テストのみ
task lint           # flake8によるコードチェック
task clean          # ビルド成果物のクリーンアップ
task serve          # 開発サーバー起動

# 新しいフロントエンドのテスト
cd packages/frontend
pnpm run build       # ビルドテスト

# 旧フロントエンド（frontend.bak）のテスト
cd packages/frontend.bak
pnpm run type-check  # TypeScript型チェック
pnpm run lint        # ESLint
pnpm run build       # ビルドテスト
```

## 技術仕様

- **バックエンド**: Python 3.12+, FastAPI, SQLAlchemy
- **フロントエンド**: 
  - **新**: React 19, TypeScript, Shadcn/UI, TanStack Router, RSBuild, Tailwind CSS
  - **旧（frontend.bak）**: React, TypeScript, Material-UI, React Router, Webpack
- **データ形式**: YAML
- **対応データベース**: MySQL (他のSQLAlchemyサポートDB)
- **スキーマ形式**: A5:SQL Mk-2, MySQL直接接続, DBGearネイティブ形式
- **スキーマ管理**: Pydanticベースの型安全なモデルによるテーブル、ビュー、インデックス、リレーション、制約の統合管理
- **MySQL特化**: パーティション、ストレージエンジン、文字セット、生成カラム等の詳細設定対応
- **型システム**: ColumnTypeオブジェクトによる厳密な型定義とMySQL全タイプサポート
- **統合ノートシステム**: 全エンティティ対応のドキュメント管理機能
- **環境管理**: DataModel、Environ、Tenant、Mappingによる包括的な環境設定
- **パッケージ管理**: Poetry (Python), pnpm (Frontend)

## ライセンス

MIT