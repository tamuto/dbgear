# データモデル定義

- データモデルは、DBGearプロジェクトの初期データを管理するための設定ファイルです。
- テーブル名をファイル名としたYAML形式のファイルで定義され、`DataModel`クラスで表現されます。
- データモデルは、スキーマ名、テーブル名、レイアウト種別、フィールド設定、同期モードなどを含みます。

## フォルダ構成

- *.yamlおよび*.datファイルがマッピングディレクトリに配置されます
  - *.yamlファイルは`{schema_name}@{table_name}.yaml`の形式で命名されます。
  - *.datファイルは`{schema_name}@{table_name}.dat`または`{schema_name}@{table_name}#{segment}.dat`の形式で命名されます。
- また、データソースはYAML以外にCSV、XLSX、Pythonスクリプトなどもサポートします。そのためファイルが存在しない可能性もあります。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 環境ディレクトリ
│   ├── environ.yaml      # 環境設定ファイル
│   ├── schema.yaml       # 環境固有スキーマ（オプション）
│   ├── tenant.yaml       # テナント設定
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

    class DataSource {
        +folder : str
        +environ : str
        +name : str
        +schema_name : str
        +table_name : str
        +segment : str | None
        +data : list[dict[str, Any]]

        +\_\_init__(folder: str, environ: str, name: str, schema_name: str, table_name: str, segment: str | None = None)

        +@ filename() : str

        +exists() bool
        +load()
        +save()
        +remove()
    }

    class YamlDataSource {
    }

    YamlDataSource --|> DataSource

    class CsvDataSource {
    }

    CsvDataSource --|> DataSource

    class XlsxDataSource {
    }

    XlsxDataSource --|> DataSource

    class PythonDataSource {
    }

    PythonDataSource --|> DataSource

    class SettingInfo {
        <<BaseSchema>>
        +setting_type : str
        +width : int | None = None
        +environ : str | None = None
        +schema_name : str | None = None
        +table_name : str | None = None
    }

    class DataParams {
        <<BaseSchema>>
        +layout : str
        +settings : dict[str, SettingInfo]
        +value : str | None = None
        +caption : str | None = None
        +segment : str | None = None
        +x_axis : str | None = None
        +y_axis : str | None = None
        +cells : list[str] | None = None

        +@ filename() : str
    }

    DataParams -- SettingInfo : settings

    class DataModel {
        <<BaseSchema>>
        +folder : str
        +environ : str
        +map_name : str
        +schema_name : str
        +table_name : str
        +description : str
        +sync_mode : str
        +data_type: str
        +data_path: str
        +data_args: dict[str, str] | None = None
        +data_params: DataParams | None = None

        +load(folder: str, environ: str, map_name: str, schema_name: str, table_name: str) DataModel$
        +save()
        +remove()
        +@ filename() str
        +@ datasources() Generic~DataSource~
    }

    DataModel -- DataSource : datasources
    DataModel -- DataParams : data_params
```
