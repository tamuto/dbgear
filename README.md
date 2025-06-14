# DBGear

データベース初期データ管理のためのローカル開発ツールです。データベースのスキーマ定義と初期データをYAML形式で管理し、Web UIを通じて直感的にデータを編集できます。

## モノレポ構成

DBGearは3つの独立したパッケージで構成されています：

- **dbgear**: コアライブラリとCLIツール
- **dbgear-web**: Webインターフェース
- **frontend**: Reactフロントエンドパッケージ

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

# フロントエンドパッケージの開発
cd packages/frontend
pnpm install
```

## 特徴

- **Web UI でのデータ編集**: 直感的なインターフェースでデータベースの初期データを編集
- **スキーマ連携**: テーブル定義に基づいたデータ入力支援と制約チェック
- **関連データ管理**: 外部キー参照の自動解決により、IDのコピペ作業が不要
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

#### 選択リスト定義
```yaml
definitions:
  - type: selectable
    prefix: _select
    items:
      status: ステータス
      category: カテゴリ
```

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
        project: プロジェクト情報
        mapping: 環境マッピング
        instance: インスタンス名
        table: テーブル名
        data_model: データモデル
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
from dbgear.core.operations import Operation

def setUp(self):
    with Operation.get_instance('./project', 'test', 'localhost') as op:
        op.reset_all()  # テストデータベースをリセット
        op.require('main', 'users')  # 必要なデータを挿入
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
# フロントエンドディレクトリに移動
cd packages/frontend

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

# フロントエンド テスト
cd packages/frontend
pnpm run type-check  # TypeScript型チェック
pnpm run lint        # ESLint
pnpm run build       # ビルドテスト
```

## 技術仕様

- **バックエンド**: Python 3.12+, FastAPI, SQLAlchemy
- **フロントエンド**: React, TypeScript, Material-UI
- **データ形式**: YAML
- **対応データベース**: MySQL (他のSQLAlchemyサポートDB)
- **スキーマ形式**: A5:SQL Mk-2, MySQL直接接続
- **パッケージ管理**: Poetry (Python), pnpm (Frontend)

## ライセンス

MIT