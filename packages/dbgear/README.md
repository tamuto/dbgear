# dbgear

[DBGear](https://github.com/tamuto/dbgear) のコアライブラリとCLIツールです。
データベースのスキーマ定義と初期データをYAMLで管理し、CLIから環境ごとにデータベースへ適用します。

プロジェクト全体の概要・クイックスタートは[リポジトリのREADME](https://github.com/tamuto/dbgear)を、
各種フォーマットの詳細仕様は [docs/](https://github.com/tamuto/dbgear/tree/main/docs) を参照してください。

## インストール

```bash
pip install dbgear

# Excelデータファイルを扱う場合
pip install dbgear[xlsx]
```

Python 3.12 以上が必要です。

## このパッケージが提供するもの

- **`dbgear` CLI** - `apply` サブコマンドによるデータベースへのスキーマ・データ適用
- **データモデル** (`dbgear.models`) - Pydanticベースのスキーマ/プロジェクト定義モデルとYAML永続化
- **データベースI/O** (`dbgear.dbio`) - Jinja2テンプレートによるSQL生成と実行(MySQL対応)
- **スキーマインポート** (`dbgear.importer`) - A5:SQL Mk-2形式などからの取り込み
- **プラグイン機構** - エントリーポイントによるCLIサブコマンドの拡張

## CLI

```bash
dbgear --project <folder> apply <deployment> <environment> [options]
```

`--all drop|delta` / `--target` / `--dryrun` などのオプションについては
[リポジトリのREADME](https://github.com/tamuto/dbgear#readme)を、
パッチファイルによる選択的データ復元の仕様は
[docs/spec_patch.md](https://github.com/tamuto/dbgear/blob/main/docs/spec_patch.md) を参照してください。

## プログラムからの利用

```python
# スキーマの読み込み・保存
from dbgear.models.schema import SchemaManager

schema_manager = SchemaManager.load('schema.yaml')
schema = schema_manager.schemas['main']
schema_manager.save('schema.yaml')

# A5:SQL Mk-2 ファイルからのインポート
from dbgear.importer import import_schema

schema_manager = import_schema('a5sql_mk2', 'path/to', 'schema.a5er', {'MAIN': 'main'})
schema_manager.save('schema.yaml')
```

主なインポートパス:

```python
from dbgear.models.project import Project
from dbgear.models.schema import SchemaManager, Schema
from dbgear.models.table import Table, TableManager
from dbgear.models.column_type import ColumnType, parse_column_type
from dbgear.models.exceptions import DBGearError
```

## パッケージ構成

```
dbgear/
├── main.py          # CLIエントリーポイント(プラグインコマンドの動的ロード)
├── operations.py    # apply処理のオーケストレーション
├── importer.py      # スキーマインポーターの動的ロード
├── models/          # Pydanticベースのデータモデル(schema, table, column, project等)
├── dbio/            # データベースI/O
│   └── templates/   # Jinja2ベースのSQLテンプレート(MySQL)
├── misc/            # A5:SQL Mk-2インポーター、依存関係分析
└── utils/           # ユーティリティ
```

## プラグインによるCLI拡張

エントリーポイント `dbgear.commands` にモジュールを登録すると、
`dbgear` CLIにサブコマンドを追加できます。

```toml
# pyproject.toml
[project.entry-points."dbgear.commands"]
my-plugin = "my_plugin.command"
```

```python
# my_plugin/command.py
def register_commands(subparsers):
    parser = subparsers.add_parser('mycommand', help='...')
    return ['mycommand']

def execute(args, project):
    ...
    return True
```

公式プラグインとして、ドキュメント・ER図生成の
[dbgear-doc](https://pypi.org/project/dbgear-doc/) があります。

## 開発

```bash
poetry install

poetry run task test    # テスト実行
poetry run task lint    # flake8によるコードチェック
```

## ライセンス

MIT
