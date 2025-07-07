# 環境定義

- DBGearプロジェクト管理下での目的に応じた環境を定義します。
- 環境では、データベース接続情報をはじめ、環境別のスキーマやテナント、マッピング情報を管理します。
- 環境は`environ.yaml`ファイルで定義され、`EnvironManager`クラスで表現されます。

## フォルダ構成

`environ.yaml`はプロジェクトの各環境ディレクトリに配置します。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 環境ディレクトリ
│   ├── environ.yaml      # 環境設定ファイル（本ファイル）
│   ├── schema.yaml       # 環境固有スキーマ（オプション）
│   ├── tenant.yaml       # テナント設定（オプション）
│   ├── mapping1/         # マッピングディレクトリ
|   |  ├── _mapping.yaml  # マッピング設定
|   |  ├── *.yaml         # データモデル定義ファイル
|   |  ├── *.dat          # データファイル
│   ├── mapping2/         # マッピングディレクトリ
|   |  ├── _mapping.yaml  # マッピング設定
|....
```

## クラス構成図

```mermaid
classDiagram
    direction LR

    class EnvironManager {
        +folder : str

        +\_\_init__(folder: str)
        +\_\_getitem__(key: str) Environ
        +\_\_iter__() Generic~Environ~
        +\_\_contains__(key: str) bool
    }

    EnvironManager -- Environ

    class Environ {
        <<BaseSchema>>
        +folder : str % exclude
        +name : str % exclude
        +description : str
        +deployments : dict[str, str] = dict

        +load(folder: str, name: str) Environ$
        +save()
        +delete()

        +@ schemas() SchemaManager | None
        +@ tenant() TenantRegistry | None
        +@ mappings() MappingManager
        +@ databases() Generic~Mapping~
    }

    Environ -- SchemaManager : schemas
    Environ -- TenantRegistry : tenant
    Environ -- MappingManager : mappings
    Environ -- Mapping : databases

    MappingManager -- Mapping
```

## 環境サンプル

```yaml
description: Environment description
deployment:
  development: mysql://dev:password@localhost:3306/myapp_dev
```
