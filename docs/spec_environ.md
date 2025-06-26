# environ.yaml 仕様書

## 概要

`environ.yaml`は、DBGearプロジェクトの環境固有設定を定義するファイルです。開発・テスト・本番などの環境ごとの説明情報を管理し、環境別のスキーマ、テナント、マッピング情報への統合アクセスを提供します。

## ファイル配置

`environ.yaml`は各環境ディレクトリ内に配置します。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 開発環境ディレクトリ
│   ├── environ.yaml      # 環境設定ファイル（本ファイル）
│   ├── schema.yaml       # 環境固有スキーマ（オプション）
│   ├── tenant.yaml       # テナント設定（オプション）
│   └── _mapping.yaml     # マッピング設定（オプション）
├── test/                 # テスト環境ディレクトリ
│   └── environ.yaml      # 環境設定ファイル
└── production/           # 本番環境ディレクトリ
    └── environ.yaml      # 環境設定ファイル
```

## 基本構造

### 必須項目

```yaml
description: Environment description
```

### オプション項目

```yaml
deployment:
  environment_name: "connection_string"
options:
  createForeignKeyConstraints: true
```

### 項目詳細

#### description
- **型**: 文字列
- **必須**: はい
- **説明**: 環境の概要説明。日本語使用可能
- **例**: `開発環境`, `テスト環境設定`, `本番環境（MySQL 8.0）`

#### deployment
- **型**: 辞書（環境名 → 接続文字列）
- **必須**: いいえ
- **デフォルト**: 空辞書 (`{}`)
- **説明**: 環境別のデータベース接続情報マッピング
- **例**: 
  - `{'production': 'mysql://user:pass@prod-host:3306/mydb'}`
  - `{'development': 'mysql://user:pass@dev-host:3306/mydb', 'staging': 'mysql://user:pass@stage-host:3306/mydb'}`

#### options
- **型**: オブジェクト
- **必須**: いいえ（未定義の場合はプロジェクト設定を継承）
- **デフォルト**: `null`（未定義）
- **説明**: 環境固有の動作制御オプション

##### options.createForeignKeyConstraints
- **型**: 真偽値
- **デフォルト**: 未定義の場合はプロジェクトの設定を継承
- **説明**: データベース構築時に外部キー制約を作成するかどうかの制御
- **継承**: 
  - 環境で定義されている場合: 環境固有の設定を使用（最優先）
  - 環境で未定義の場合: プロジェクトレベルのオプション設定を継承
- **用途**: 
  - `true`: 通常の運用環境で外部キー制約を有効化
  - `false`: テスト環境やデータ投入時の制約回避
  - 未定義: プロジェクト設定に従う

## 関連ファイル

環境ディレクトリには以下のファイルが配置される場合があります：

#### schema.yaml
- **説明**: 環境固有のスキーマ定義（存在する場合はプロジェクトルートのschema.yamlより優先）
- **用途**: 環境ごとのテーブル構造やデータ定義の差分管理

#### tenant.yaml
- **説明**: マルチテナント設定
- **用途**: テナント別のデータベース接続情報とプレフィックス管理

#### _mapping.yaml
- **説明**: マッピング設定
- **用途**: データベース接続とスキーマインスタンスのマッピング定義

## 設定例

### 開発環境の設定例（プロジェクト設定を継承）

```yaml
description: 開発環境
deployment:
  development: "mysql://dev:password@localhost:3306/myapp_dev"
# options: 未定義（プロジェクト設定を継承）
```

### テスト環境の設定例（制約無効化）

```yaml
description: テスト環境設定
deployment:
  testing: "mysql://test:password@test-server:3306/myapp_test"
  staging: "mysql://stage:password@stage-server:3306/myapp_stage"
options:
  createForeignKeyConstraints: false  # テスト環境では制約を無効化
```

### 本番環境の設定例

```yaml
description: 本番環境（MySQL 8.0）
deployment:
  production: "mysql://prod:secret@prod-server:3306/myapp"
options:
  createForeignKeyConstraints: true  # 本番環境では制約を有効化
```

### 開発環境の詳細設定例

```yaml
description: 開発環境（デバッグ用）
deployment:
  development: "mysql://dev:password@localhost:3306/myapp_dev"
  local_test: "mysql://test:password@localhost:3306/myapp_test"
options:
  createForeignKeyConstraints: false  # 開発時は制約を無効化してデバッグを容易に
```

## 環境管理

環境は`EnvironManager`によって管理され、以下の機能を提供します：

- **遅延読み込み**: 環境固有のスキーマ、テナント、マッピング情報の効率的な管理
- **統合アクセス**: `Project.envs[環境名]`による環境情報への一元アクセス
- **自動検出**: 環境ディレクトリの自動探索と環境一覧の取得
- **オプション継承**: プロジェクトレベルのオプション設定を継承し、必要に応じて環境固有のオプションで上書き可能

### オプション管理

環境固有のオプション設定は以下の優先順位で適用されます：

1. **環境固有設定**: `environ.yaml`内の`options`セクション（最優先）
2. **プロジェクト設定**: `project.yaml`内の`options`セクション（継承）

環境で`options`が未定義（`null`）の場合、プロジェクト設定が自動的に継承されます。これにより、プロジェクト全体で共通のオプション設定を維持しながら、特定の環境でのみ異なる設定を適用することが可能です。

この仕様により、DBGearプロジェクトの環境別設定を統一的に管理できます。