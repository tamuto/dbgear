# project.yaml 仕様書

## 概要

`project.yaml`は、DBGearプロジェクトの基本情報を定義する設定ファイルです。プロジェクトの識別名と説明を管理し、DBGearの各種機能の起点となります。

## ファイル配置

`project.yaml`はプロジェクトのルートディレクトリに配置します。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル（本ファイル）
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 開発環境ディレクトリ
├── test/                 # テスト環境ディレクトリ
└── production/           # 本番環境ディレクトリ
```

## 基本構造

### 必須項目

```yaml
project_name: MyProject
description: Database initial data management
options:
  createForeignKeyConstraints: true
```

### 項目詳細

#### project_name
- **型**: 文字列
- **必須**: はい
- **説明**: プロジェクトの識別名。英数字とアンダースコアの使用を推奨
- **例**: `MyProject`, `ecommerce_app`, `user_management`

#### description
- **型**: 文字列
- **必須**: はい
- **説明**: プロジェクトの概要説明。日本語使用可能
- **例**: `ユーザー管理システムのデータベース`, `ECサイトの初期データ管理`

#### options
- **型**: オブジェクト
- **必須**: いいえ（デフォルト値使用）
- **説明**: プロジェクト全体での動作制御オプション

##### options.createForeignKeyConstraints
- **型**: 真偽値
- **デフォルト**: `true`
- **説明**: データベース構築時に外部キー制約を作成するかどうかの制御
- **用途**: 
  - `true`: 通常の運用環境で外部キー制約を有効化
  - `false`: テスト環境やデータ投入時の制約回避

## 設定例

### 基本的な設定例

```yaml
project_name: MyApp
description: My Application Database
```

### デフォルトオプション使用例

```yaml
project_name: MyApp
description: My Application Database
options:
  createForeignKeyConstraints: true
```

### テスト環境向け設定例

```yaml
project_name: MyApp_Test
description: My Application Database (Test Environment)
options:
  createForeignKeyConstraints: false  # テスト時は制約を無効化
```

### 実際のプロジェクト例

```yaml
project_name: ecommerce_system
description: ECサイトのデータベース初期データ管理プロジェクト
options:
  createForeignKeyConstraints: true  # 本番環境では制約を有効化
```

```yaml
project_name: user_management
description: ユーザー管理システムのスキーマとマスターデータ定義
options:
  createForeignKeyConstraints: false  # 大量データ投入のため制約を無効化
```

この仕様により、DBGearプロジェクトの基本設定を統一的に管理できます。