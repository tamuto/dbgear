# データマッピング定義

- DBGearの環境毎のデータとのマッピングを定義します。
- マッピングは、スキーマとデータベースの関連付けを行い、初期データの管理を行います。
- データマッピングは`_mapping.yaml`ファイルで定義され、`MappingManager`クラスで表現されます。

## フォルダ構成

`_mapping.yaml`は各環境ディレクトリ内のマッピングサブディレクトリに配置します。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 環境ディレクトリ
│   ├── environ.yaml      # 環境設定ファイル
│   ├── schema.yaml       # 環境固有スキーマ（オプション）
│   ├── tenant.yaml       # テナント設定（オプション）
│   ├── mapping1/         # マッピングディレクトリ
|   |  ├── _mapping.yaml  # マッピング設定（本ファイル）
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

    class Mapping {
        <<BaseSchema>>
        +folder : str % exclude
        +environ : str % exclude
        +name : str % exclude
        +tenant_name : str | None = None % exclude
        +description : str
        +schemas : list[str] = []
        +deploy : bool = False

        +load(folder: str, environ: str, name: str) Mapping$

        +save()
        +delete()
        +build_schema(project_schema: SchemaManager, environ_schema: SchemaManager | None) Schema

        +@ instance_name() str
        +datamodels() Generic~DataModel~
        +datamodel(schema_name: str, table_name: str) DataModel
    }

    Mapping -- DataModel
    Mapping -- Schema

    class MappingManager {
        -folder : str
        -environ : str

        +\_\_init__(folder: str, environ: str)
        +\_\_getitem__(key: str) Mapping
        +\_\_iter__() Generic~Mapping~
        +\_\_contains__(key: str) bool
    }

    MappingManager -- Mapping
```

## サンプル

```yaml
description: Mapping description
schemas:
  - schema_name
deploy: true
```
