# 変数展開 (Settings)

- DBGearでは、データ投入時に `$変数名` 形式の変数を展開する機能を提供します。
- 環境（Environ）やテナント（DatabaseInfo）で定義した設定値、およびDataModelのコンテキスト値を変数として参照できます。
- データファイル（`.dat`、`.xlsx`等）の値や、DataModelの `data_path`・`data_args` で利用可能です。

## 変数の定義場所

### 環境設定 (environ.yaml)

`settings` フィールドで環境共通の変数を定義します。

```yaml
description: Production environment
deployments:
  localhost: mysql+pymysql://root:password@localhost?charset=utf8mb4
settings:
  app_name: MyApplication
  base_url: https://example.com
  admin_email: admin@example.com
```

### テナント設定 (tenant.yaml)

`DatabaseInfo` の `settings` フィールドでテナント固有の変数を定義します。

```yaml
tenants:
  multi:
    ref: base
    databases:
      - database: tenant_a
        settings:
          app_name: TenantA App
          base_url: https://a.example.com
      - database: tenant_b
        settings:
          app_name: TenantB App
          base_url: https://b.example.com
```

### コンテキスト変数

DataModel処理時に以下の値が自動的に変数として利用可能になります。

| 変数名 | 説明 |
|---|---|
| `$folder` | プロジェクトフォルダパス |
| `$environ` | 環境名 |
| `$map_name` | マッピング名 |
| `$schema_name` | スキーマ名 |
| `$table_name` | テーブル名 |
| `$tenant_name` | テナント名（テナント構成時のみ） |

## 変数の優先順位

同名の変数が複数の場所で定義されている場合、以下の優先順位で解決されます。

```
コンテキスト変数 < Environ.settings < DatabaseInfo.settings（テナント）
```

高い優先順位の値が低い優先順位の値を上書きします。

## 変数展開の構文

### 基本構文

`$変数名` で変数を参照します。変数名には英数字とアンダースコアが使用可能です。

```yaml
- name: $app_name
  url: $base_url/api/v1
```

### エスケープ

`$$変数名` と書くことで展開を抑制し、リテラルの `$変数名` として出力します。

```yaml
- expr: $$app_name       # → "$app_name"（展開されない）
```

### 未定義変数

settingsに定義されていない変数はそのまま保持されます。

```yaml
- value: $undefined       # → "$undefined"（変更なし）
```

## 展開される箇所

変数展開は `apply` コマンド実行時の以下の箇所で適用されます。

### 1. データファイルの値

`.dat`（YAML）や `.xlsx` 等、全てのDataSourceで読み込まれたデータ値に適用されます。

```yaml
# main@config.dat
- key: app_name
  value: $app_name
- key: contact
  value: $admin_email
- key: source
  value: $schema_name@$table_name
```

### 2. DataModelの data_path

```yaml
# main@users.yaml
description: User master
sync_mode: drop_create
data_type: xlsx
data_path: $folder/shared/master.xlsx
```

### 3. DataModelの data_args

```yaml
# main@users.yaml
description: User master
sync_mode: drop_create
data_type: xlsx
data_path: master.xlsx
data_args:
  sheet: $table_name
  header_row: 1
  start_row: 2
```

## 使用例

### 環境別の設定値をデータに埋め込む

```yaml
# environ.yaml (development)
settings:
  base_url: http://localhost:8080
  storage_path: /tmp/dev-storage

# environ.yaml (production)
settings:
  base_url: https://api.example.com
  storage_path: /mnt/production-storage
```

```yaml
# main@system_config.dat
- config_key: api_endpoint
  config_value: $base_url/api/v1
- config_key: file_storage
  config_value: $storage_path/uploads
```

### テナント別の設定値

```yaml
# tenant.yaml
tenants:
  multi:
    ref: base
    databases:
      - database: company_a_db
        settings:
          company_name: Company A
          company_code: A001
      - database: company_b_db
        settings:
          company_name: Company B
          company_code: B001
```

```yaml
# main@company_info.dat
- id: 1
  name: $company_name
  code: $company_code
```

### コンテキスト変数の活用

```yaml
# main@audit_log.dat（テナント構成時）
- table_ref: $schema_name@$table_name
  tenant: $tenant_name
  description: Initial data for $table_name
```

### エスケープとの組み合わせ

```yaml
# main@templates.dat
- id: 1
  template: Hello $$user_name, welcome to $app_name
  # → "Hello $user_name, welcome to MyApplication"
  # $user_name はリテラル、$app_name は展開
```

## クラス構成図

```mermaid
classDiagram
    direction TB

    class Environ {
        +settings : dict[str, str]
    }

    class DatabaseInfo {
        +settings : dict[str, str]
    }

    class Mapping {
        +settings : dict[str, str] % exclude
    }

    class DataModel {
        +build_settings(settings) dict[str, str]
        +get_datasources(settings) Generic~DataSource~
    }

    Environ --> DataModel : environ.settings
    DatabaseInfo --> Mapping : materialize時に伝搬
    Mapping --> DataModel : map.settings
    DataModel --> DataSource : 展開済みdata_path, data_args
    DataSource --> Operation : 展開済みデータ値
```

## 注意事項

- 変数展開は `apply` コマンドによるデータ投入時にのみ実行されます。YAMLファイル自体は変更されません。
- ネストした辞書（JSON型カラム等）内の文字列値も再帰的に展開されます。
- リスト型の値は展開対象外です。
- `settings` の値は全て文字列型（`dict[str, str]`）です。
