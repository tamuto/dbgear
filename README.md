# DBGear

データベースのスキーマ定義と初期データをYAMLで管理するためのローカル開発ツールです。
スキーマとデータをコードとして(Git等で)バージョン管理し、CLIから環境ごとにデータベースへ適用できます。

## 特徴

- **YAMLベースのスキーマ管理** - テーブル・ビュー・トリガー・プロシージャ・インデックス・外部キーをYAMLで定義
- **初期データ管理** - 環境(dev/test/prod等)ごとの初期データを `.dat` ファイルで管理し、依存関係を解決した順序で投入
- **差分適用** - `--all delta` による前回適用からの差分適用、`--target` による特定テーブルのみの適用
- **バックアップ/リストア** - 適用時の自動バックアップと、パッチファイルによる選択的なデータ復元
- **SQLテンプレートエンジン** - Jinja2ベースのテンプレートによる保守性の高いSQL生成(MySQL対応)
- **A5:SQL Mk-2 インポート** - `.a5er` ファイルからのスキーマ取り込み
- **JSONカラム対応** - YAMLの辞書データをMySQL JSON型へ自動変換して投入
- **プラグインシステム** - エントリーポイント `dbgear.commands` によるCLIサブコマンドの拡張

## パッケージ構成

本リポジトリはモノレポ構成で、以下のパッケージを含みます。

| パッケージ | 説明 |
|-----------|------|
| [dbgear](./packages/dbgear/) | コアライブラリとCLIツール(スキーマ管理・データベース適用) |
| [dbgear-doc](./packages/dbgear-doc/) | ドキュメント生成プラグイン(Markdownドキュメント・ER図のSVG/draw.io出力) |

dbgear-doc のER図生成には [in4viz](https://github.com/tamuto/in4viz) ライブラリを使用しています。

## インストール

```bash
pip install dbgear

# ドキュメント・ER図生成機能を使う場合
pip install dbgear-doc
```

Python 3.12 以上が必要です。

## クイックスタート

### プロジェクト構成

```
my-database/
├── project.yaml          # プロジェクト定義(バインディング・ルール・デプロイ先)
├── schema.yaml           # スキーマ定義
├── diagram.yaml          # ER図のカテゴリ別スタイル設定(任意)
└── env1/                 # 環境ディレクトリ
    ├── environ.yaml      # 環境定義
    └── instance1/        # インスタンス(データセット)
        ├── main@users.yaml   # データ設定
        └── main@users.dat    # 初期データ(YAML形式)
```

### スキーマ定義の例

```yaml
schemas:
  main:
    tables:
      users:
        displayName: ユーザー
        columns:
        - columnName: id
          columnType:
            columnType: BIGINT
            baseType: BIGINT
          nullable: false
          primaryKey: 0
        - columnName: name
          columnType:
            columnType: VARCHAR(100)
            baseType: VARCHAR
            length: 100
          nullable: false
```

### データベースへの適用

```bash
# 全テーブルを削除して再作成
dbgear --project my-database apply localhost development --all drop

# 前回適用からの差分のみ適用
dbgear --project my-database apply localhost development --all delta

# 特定のテーブルのみ適用
dbgear --project my-database apply localhost development --target users

# SQLを実行せずに確認(ドライラン)
dbgear --project my-database apply localhost development --all drop --dryrun
```

主なオプション:

| オプション | 説明 |
|-----------|------|
| `--all drop\|delta` | 全テーブルへの適用(drop: 再作成 / delta: 差分適用) |
| `--target <table>` | 特定テーブルのみ適用 |
| `--no-restore` | データ投入・復元をスキップ |
| `--restore-only` | スキーマ再作成なしでデータ復元のみ |
| `--patch <file>` | パッチファイルによる選択的データ復元 |
| `--index-only` | インデックスのみ再作成(`--target` 必須) |
| `--dryrun` | SQLを出力するのみで実行しない |

## ドキュメント・ER図の生成(dbgear-doc)

dbgear-doc をインストールすると `doc` / `svg` / `drawio` サブコマンドが追加されます。

```bash
# Jinja2テンプレートからテーブル定義書を生成
dbgear --project my-database doc -o ./output --template table.md.j2 --scope table

# ER図をSVG形式で出力
dbgear --project my-database svg -o er_diagram.svg

# 特定テーブルを中心に、参照関係を辿った範囲のER図を出力
dbgear --project my-database svg -t users --referenced-by-level 2 --references-level 1

# draw.io形式で出力(draw.ioで編集可能)
dbgear --project my-database drawio -o er_diagram.drawio
```

`diagram.yaml` を配置すると、テーブルのカテゴリごとに背景色を設定できます。

```yaml
categories:
  master:
    background_color: "#E3F2FD"
    use_gradient: true
  transaction:
    background_color: "#FFF3E0"
default:
  background_color: "#FFFFFF"
```

## プログラムからの利用

```python
from dbgear.models.schema import SchemaManager

# スキーマの読み込み・編集・保存
schema_manager = SchemaManager.load('schema.yaml')
schema = schema_manager.schemas['main']
schema_manager.save('schema.yaml')

# A5:SQL Mk-2 ファイルからのインポート
from dbgear.importer import import_schema
schema_manager = import_schema('a5sql_mk2', 'path/to', 'schema.a5er', {'MAIN': 'main'})
```

## 開発

各パッケージは Poetry で管理されています。

```bash
cd packages/dbgear
poetry install

# テスト実行
poetry run task test

# Lint
poetry run task lint
```

## ドキュメント

詳細な仕様は [docs/](./docs/index.md) を参照してください。

- [プロジェクト定義](./docs/spec_project.md)
- [データベーススキーマ定義](./docs/spec_schema.md)
- [環境定義](./docs/spec_environ.md)
- [データモデル設定](./docs/spec_datamodel.md)
- [パッチ機能](./docs/spec_patch.md)
- [依存関係管理](./docs/spec_dependencies.md)

## ライセンス

[MIT License](./LICENSE)
