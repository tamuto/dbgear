# tenant.yaml 仕様書

## 概要

`tenant.yaml`は、DBGearプロジェクトのマルチテナント設定を定義するファイルです。テナント別のデータベース接続情報、プレフィックス設定、データベース定義を管理し、環境ごとのマルチテナント運用を支援します。

## ファイル配置

`tenant.yaml`は各環境ディレクトリ内に配置します。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 開発環境ディレクトリ
│   ├── environ.yaml      # 環境設定ファイル
│   └── tenant.yaml       # テナント設定ファイル（本ファイル）
├── test/                 # テスト環境ディレクトリ
│   └── tenant.yaml       # テナント設定ファイル
└── production/           # 本番環境ディレクトリ
    └── tenant.yaml       # テナント設定ファイル
```

## 基本構造

### 必須項目

```yaml
tenants:
  tenant_name:
    name: tenant_name
    ref: reference_name
    databases: []
```

### 項目詳細

#### tenants
- **型**: オブジェクト
- **必須**: はい
- **説明**: テナント設定のコレクション

#### name
- **型**: 文字列
- **必須**: はい
- **説明**: テナントの識別名
- **例**: `localhost`, `docker`, `production`

#### ref
- **型**: 文字列
- **必須**: はい
- **説明**: 参照名（テナント間の関係定義）
- **例**: `base`, `main`, `primary`

#### prefix
- **型**: 文字列
- **必須**: いいえ
- **デフォルト**: 空文字列
- **説明**: テーブル名やデータベース名に付加するプレフィックス
- **注意**: 現在のモデルでは`prefix`フィールドは削除されました
- **例**: `dev_`, `test_`, `prod_`

#### databases
- **型**: リスト
- **必須**: いいえ
- **説明**: データベース定義のリスト
- **子要素**:
  - `name`: データベースの論理名
  - `database`: 実際のデータベース名
  - `description`: データベースの説明
  - `active`: アクティブフラグ（true/false）

## 設定例

### 基本的なテナント設定

```yaml
tenants:
  localhost:
    name: localhost
    ref: base
    databases:
      - name: main
        database: testdb
        description: Test database
        active: true
```

### 複数データベース設定

```yaml
tenants:
  production:
    name: production
    ref: main
    databases:
      - name: main
        database: app_production
        description: Production database
        active: true
      - name: backup
        database: app_backup
        description: Backup database
        active: false
```

## テナント管理

テナントは`TenantRegistry`によって管理され、以下の機能を提供します：

- **CRUD操作**: テナント設定の追加・削除・更新・参照
- **YAML永続化**: 設定変更の自動保存機能
- **統合アクセス**: `Environment.tenants[テナント名]`によるテナント情報への直接アクセス
- **バリデーション**: Pydanticベースの型安全な設定管理

この仕様により、DBGearプロジェクトのマルチテナント設定を統一的に管理できます。