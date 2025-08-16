# DBGear

データベース初期データ管理のためのローカル開発ツールです。データベースのスキーマ定義と初期データをYAML形式で管理し、Web UIを通じて直感的にデータを編集できます。

## 📚 ドキュメンテーション

詳細な仕様と使用方法については、[ドキュメンテーション](docs/index.md)をご覧ください。

## モノレポ構成

DBGearは3つの独立したパッケージで構成されています：

- **dbgear**: コアライブラリとCLIツール（A5:SQL Mk-2インポート機能を内蔵）
- **dbgear-editor**: FastHTML-based Webエディター（スキーマ閲覧・編集）
- **dbgear-mcp**: LLM統合のためのMCPサーバー

## インストール

### CLI使用（コアライブラリ）
```bash
pip install dbgear
```

### Web エディター使用
```bash
pip install dbgear-editor  # 自動的にdbgearもインストールされます
```

### 開発用インストール
```bash
# リポジトリをクローン
git clone https://github.com/tamuto/dbgear.git
cd dbgear

# CLIパッケージの開発
cd packages/dbgear
poetry install

# Webエディターパッケージの開発
cd packages/dbgear-editor
poetry install
```

## 特徴

- **Web エディターでのスキーマ閲覧**: FastHTML-based の直感的なインターフェースでデータベーススキーマを閲覧・編集
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
# A5:SQL Mk-2 ファイルからスキーマ定義をインポート（内蔵機能）
dbgear import a5sql_mk2 schema.a5er --output schema.yaml

# データベースへの適用
dbgear apply localhost development --all drop

# 差分のみ適用
dbgear apply localhost development --all delta

# 特定のテーブルのみ適用
dbgear apply localhost development --target users
```

### 4. Web エディター使用

```bash
# Webエディターサーバーの起動
dbgear-editor --project . --port 8000

# 開発モード（自動リロード）
dbgear-editor --project ./my-project --port 8000 --reload
```

ブラウザで http://localhost:8000 にアクセスして、Web エディターでスキーマを閲覧します。

## 設定ファイル

各設定ファイルの詳細については、以下のドキュメントをご確認ください：

- [project.yaml](docs/spec_project.md) - プロジェクトルート設定
- [schema.yaml](docs/spec_schema.md) - データベーススキーマ定義
- [environ.yaml](docs/spec_environ.md) - 環境固有設定
- [_mapping.yaml](docs/spec_mapping.md) - マッピング設定
- [tenant.yaml](docs/spec_tenant.md) - マルチテナント設定
- [DataModel.yaml](docs/spec_datamodel.md) - データモデル設定

## スキーマ定義

DBGearでは、YAML形式でテーブル、ビュー、インデックス、リレーションを定義できます。詳細な仕様については[schema.yaml仕様](docs/spec_schema.md)をご確認ください。

## アーキテクチャ

DBGearは、Pydanticベースの型安全なデータモデルシステムを採用し、包括的なデータベーススキーマ管理を実現しています。詳細については[コアモデル仕様](docs/spec_model.md)をご確認ください。

主な特徴：
- **Pydanticベース**: 自動検証とYAMLシリアライゼーション
- **Managerパターン**: 統一されたCRUD操作インターフェース
- **型安全性**: TypeScriptライクな完全な型ヒント
- **MySQL重視**: 包括的なMySQL機能サポート

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

## Web エディターコマンド

### dbgear-editor
Web エディターサーバーを起動します。

```bash
# 基本構文
dbgear-editor --project PROJECT_DIR [options]

# オプション
--project PROJECT_DIR  # プロジェクトディレクトリ (必須)
--port PORT            # ポート番号 (デフォルト: 8000)
--host HOST            # ホスト名 (デフォルト: 127.0.0.1)
--reload               # 開発モード（自動リロード有効）
```

## プラグイン開発

カスタムデータ変換ロジックをプラグインとして実装できます。詳細は[ドキュメンテーション](docs/index.md)をご確認ください。

## 開発環境セットアップ

### Web エディター開発

```bash
# Webエディターディレクトリに移動
cd packages/dbgear-editor

# 依存関係をインストール
poetry install

# 開発サーバー起動（ポート8000、自動リロード有効）
poetry run dbgear-editor --project ../../etc/test --port 8000 --reload

# Lintチェック
task lint
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

# Web エディターパッケージのテスト
cd packages/dbgear-editor
task lint           # flake8によるコードチェック
task clean          # ビルド成果物のクリーンアップ
task serve          # 開発サーバー起動

# MCPパッケージのテスト
cd packages/dbgear-mcp
task test           # 全テスト実行
task test-fast      # 軽量テストのみ
task lint           # flake8によるコードチェック
task clean          # ビルド成果物のクリーンアップ
task serve          # MCPサーバー起動
```

## 技術仕様

- **バックエンド**: Python 3.12+, SQLAlchemy, Jinja2-based SQL template engine
- **Web エディター**: FastHTML, MonsterUI, Tailwind CSS (サーバーサイドレンダリング)
- **MCPサーバー**: FastMCP, LLM統合機能
- **データ形式**: YAML
- **対応データベース**: MySQL (他のSQLAlchemyサポートDB)
- **スキーマ形式**: A5:SQL Mk-2 (内蔵インポート), MySQL直接接続, DBGearネイティブ形式
- **スキーマ管理**: Pydanticベースの型安全なモデルによるテーブル、ビュー、インデックス、リレーション、制約の統合管理
- **MySQL特化**: パーティション、ストレージエンジン、文字セット、生成カラム等の詳細設定対応
- **型システム**: ColumnTypeオブジェクトによる厳密な型定義とMySQL全タイプサポート
- **統合ノートシステム**: 全エンティティ対応のドキュメント管理機能
- **環境管理**: DataModel、Environ、Tenant、Mappingによる包括的な環境設定
- **パッケージ管理**: Poetry (Python)

## ライセンス

MIT