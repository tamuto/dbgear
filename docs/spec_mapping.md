# _mapping.yaml 仕様書

## 概要

`_mapping.yaml`は、DBGearプロジェクトのマッピング設定を定義するファイルです。環境内のデータベースインスタンス、デプロイメント設定、説明情報を管理し、環境とスキーマインスタンスの関連付けを提供します。

## ファイル配置

`_mapping.yaml`は各環境ディレクトリ内のマッピングサブディレクトリに配置します。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 開発環境ディレクトリ
│   ├── environ.yaml      # 環境設定ファイル
│   ├── base/             # ベースマッピングディレクトリ
│   │   ├── _mapping.yaml # マッピング設定ファイル（本ファイル）
│   │   └── *.yaml        # データファイル群
│   └── test1/            # テスト1マッピングディレクトリ
│       ├── _mapping.yaml # マッピング設定ファイル
│       └── *.yaml        # データファイル群
└── production/           # 本番環境ディレクトリ
    └── main/             # メインマッピングディレクトリ
        └── _mapping.yaml # マッピング設定ファイル
```

## 基本構造

### 必須項目

```yaml
instances:
  - instance_name
description: Mapping description
deploy: false
```

### 項目詳細

#### instances
- **型**: リスト
- **必須**: はい
- **説明**: このマッピングが対象とするスキーマインスタンス名のリスト
- **例**: `[main]`, `[main, secondary]`, `[user_db, log_db]`

#### description
- **型**: 文字列
- **必須**: はい
- **説明**: マッピングの概要説明。日本語使用可能
- **例**: `ベースデータベース`, `テスト用データベース`, `本番環境メインDB`

#### deploy
- **型**: ブール値
- **必須**: いいえ
- **デフォルト**: false
- **説明**: デプロイメント対象フラグ
- **用途**: 
  - `true`: 実際のデプロイメント処理で使用される
  - `false`: テスト用やバックアップ用（デプロイメント対象外）

## 設定例

### ベースマッピング設定

```yaml
instances:
  - main
description: ベースデータベース
deploy: false
```

### デプロイメント対象設定

```yaml
instances:
  - main
description: 本番環境メインデータベース
deploy: true
```

### 複数インスタンス設定

```yaml
instances:
  - main
  - secondary
description: マルチインスタンス環境
deploy: true
```

## マッピング管理

マッピングは`MappingManager`によって管理され、以下の機能を提供します：

- **CRUD操作**: マッピング設定の追加・削除・更新・参照
- **ディレクトリ管理**: マッピングディレクトリの自動作成・削除
- **統合アクセス**: `Environment.mappings[マッピング名]`によるマッピング情報への直接アクセス
- **データファイル管理**: マッピングディレクトリ内のデータファイル群の管理

この仕様により、DBGearプロジェクトのマッピング設定を統一的に管理できます。