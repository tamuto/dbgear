# DBGear

データベース初期データ管理のためのローカル開発ツールです。データベースのスキーマ定義と初期データをYAML形式で管理し、Web UIを通じて直感的にデータを編集できます。

## 📚 ドキュメンテーション

詳細な仕様と使用方法については、[ドキュメンテーション](docs/index.md)をご覧ください。

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

カスタムデータ変換ロジックをプラグインとして実装できます。詳細は[ドキュメンテーション](docs/index.md)をご確認ください。

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