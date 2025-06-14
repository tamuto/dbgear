# DBGear

データベース初期データ管理のためのコアライブラリとCLIツールです。

## インストール

```bash
pip install dbgear
```

## 使用方法

### CLIコマンド

```bash
# データベースへの適用
dbgear apply <deployment> <environment> [options]

# 例：全テーブルを削除して再作成
dbgear apply localhost development --all drop

# 例：差分のみ適用
dbgear apply localhost development --all delta

# 例：特定のテーブルのみ適用
dbgear apply localhost development --target users
```

### プログラムでの利用

```python
from dbgear.core.models.project import Project
from dbgear.core.operations import Operation

# プロジェクト読み込み
project = Project("./my-project")
project.read_definitions()

# データベース操作
with Operation(project, "development", "localhost") as op:
    op.reset_all()  # 全テーブルをリセット
    op.require("main", "users")  # 特定のテーブルデータを挿入
```

## 機能

- **データベーススキーマ管理**: A5:SQL Mk-2、MySQL直接接続対応
- **初期データ管理**: YAML形式でのデータ定義
- **環境管理**: 開発・テスト・本番環境の分離
- **データバインディング**: 自動的な値設定（UUID、現在時刻等）
- **プラグイン機構**: カスタムデータ変換の拡張

## プロジェクト構成

### project.yaml
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

deployments:
  localhost: mysql+pymysql://root:password@localhost/mydb
```

### 環境設定
```yaml
# development/_mapping.yaml
id: mydb_dev
instances:
  - main
```

## ライブラリ構成

- `dbgear.core.models`: データモデルとプロジェクト管理
- `dbgear.core.dbio`: データベースI/O操作
- `dbgear.core.definitions`: スキーマ定義パーサー
- `dbgear.core.operations`: データベース操作オーケストレーション
- `dbgear.cli`: CLIインターフェース

## Web UIが必要な場合

Web UIでのデータ編集が必要な場合は、`dbgear-web`パッケージをインストールしてください：

```bash
pip install dbgear-web
dbgear-web --project ./my-project --port 5000
```

## 開発

### テスト実行
```bash
task test           # 全テスト実行
task test-fast      # 軽量テストのみ
task lint           # flake8によるコードチェック
task clean          # ビルド成果物のクリーンアップ
```

### 依存関係
```bash
poetry install      # 依存関係のインストール
poetry add package  # パッケージの追加
```

## ライセンス

MIT