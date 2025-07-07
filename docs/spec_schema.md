# スキーマ定義

- DBGearのデータベーススキーマ定義を管理するファイルです。
- テーブル、ビュー、トリガー、インデックス、リレーション、カラム型定義を包括的に管理し、DBGearの中核となるスキーマ情報を提供します。

## フォルダ構成

- `schema.yaml`はプロジェクトのルートディレクトリに配置します。
- また、環境ごとに異なるスキーマ定義が必要な場合は、各環境ディレクトリ内に`schema.yaml`を配置することもできます。

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

### スキーマ

```mermaid
classDiagram
    direction LR

    class ColumnTypeRegistry {
        -types : dict[str, ColumnType]

        +\_\_init__(types: dict[str, ColumnType])
        +\_\_getitem__(key: str) ColumnType
        +\_\_iter__() Generic~ColumnType~
        +\_\_len__() int
        +\_\_contains__(key: str) bool

        +append(column_type: ColumnType)
        +remove(column_type: str)
    }

    ColumnTypeRegistry -- ColumnType

    class Schema {
        <<BaseSchema>>
        +name : str
        +tables_ : dict[str, Table] = dict
        +views_ : dict[str, View] = dict
        +triggers_ : dict[str, Trigger] = dict
        +notes_ : list[Note] = []

        +@ tables() TableManager
        +@ views() ViewManager
        +@ triggers() TriggerManager
        +@ notes() NoteManager

        +merge(other: Schema)
    }

    Schema -- TableManager : tables
    Schema -- ViewManager : views
    Schema -- TriggerManager : triggers
    Schema -- NoteManager : notes

    class SchemaManager {
        <<BaseSchema>>
        +schemas : dict[str, Schema]
        +registry_ : dict[str, ColumnType] = dict
        +notes_ : list[Note] = []

        +load(filename: str) SchemaManager$
        +save(filename: str)

        +\_\_getitem__(name: str) Schema
        +\_\_iter__() Generic~Schema~
        +\_\_len__() int
        +\_\_contains__(name: str) bool

        +append(schema: Schema)
        +remove(name: str)

        +@ registry() ColumnTypeRegistry
        +@ notes() NoteManager
    }

    SchemaManager -- Schema
    SchemaManager -- ColumnTypeRegistry : registry
    SchemaManager -- NoteManager : notes


```

### テーブル、カラム、インデックス

```mermaid
classDiagram
    class Column {
        <<BaseSchema>>
        +column_name : str
        +display_name : str
        +column_type : ColumnType
        +nullable : bool
        +primary_key : int | None = None
        +default_value : str | None = None

        +expression : str | None = None
        +stored : bool = False
        +auto_increment : bool = False
        +charset : str | None = None
        +collation : str | None = None
        +notes_ : list[Note] = []

        +@ notes() NoteManager
    }

    Column -- ColumnType : column_type
    Column -- NoteManager : notes

    class ColumnTypeItem {
        <<BaseSchema>>
        +value : str
        +caption_ : str | None = None
        +description : str | None = None
        +from_string(value: str) ColumnTypeItem$
        +from_dict(data: dict) ColumnTypeItem$

        +@ caption() : str
    }

    class ColumnManager {
        -columns : list[Column]

        +\_\_init__(columns: list[Column])
        +\_\_getitem__(key: int | str) Column
        +\_\_iter__() Generic~Column~
        +\_\_len__() int

        +add(column: Column)
        +remove(column: Column)
    }

    ColumnManager -- Column

    class ColumnType {
        <<BaseSchema>>
        +column_type : str
        +base_type : str
        +length : int | None = None
        +precision : int | None = None
        +scale : int | None = None
        +items : list[ColumnTypeItem] | None = None
        +json_schema : dict | None = None

        +get_item_values() list[str]
        +add_item(item: str | dict | ColumnTypeItem)
        +remove_item(value: str) bool
    }

    ColumnType -- ColumnTypeItem : items

    class Index {
        <<BaseSchema>>
        +index_name : str
        +columns : list[str]
        +index_type : str = "BTREE"
        +unique : bool = False
        +partial_condition : str | None = None
        +include_columns : list[str] | None = None
        +storage_parameters : dict[str, str] | None = NOne
        +tablespace : str | None = None
        +notes_ : list[Note]

        +@ notes() NoteManager
    }

    Index -- NoteManager : notes

    class IndexManager {
        -indexes : list[Index]

        +__init__(indexes: list[Index])
        +__getitem__(index: int) Index
        +__iter__() Generic~Index~
        +__len__() int

        +add(index: Index)
        +remove(index: Index)
    }

    IndexManager -- Index


    class MySQLTableOptions {
        +engine : str = "InnoDB"
        +charset : str | None = None
        +collation : str | None = None
        +auto_increment : int | None = None
        +row_format : str | None = None
        +partition_by : str | None = None
        +partition_expression : str | None = None
        +partition_count : int | None = None
    }

    class Table {
        +table_name : str
        +display_name : str
        +columns_ : list[Column]
        +indexes_ : list[Index]
        +relations_ : list[Relation]
        +notes_ : list[Note]
        +mysql_options : MySQLTableOptions | None

        +@ columns() ColumnManager
        +@ indexes() IndexManager
        +@ relations() RelationManager
        +@ notes() NoteManager
    }

    Table -- ColumnManager : columns
    Table -- IndexManager : indexes
    Table -- RelationManager : relations
    Table -- NoteManager : notes
    Table -- MySQLTableOptions : mysql_options

    class TableManager {
        -tables : dict[str, Table]

        +\_\_init__(tables: dict[str, Table])
        +\_\_getitem__(table_name: str) Table
        +\_\_iter__() Generic~Table~
        +\_\_len__() int
        +\_\_contains__(table_name: str) bool

        +keys()
        +values()
        +items()

        +add(table: Table)
        +remove(table_name: str)
    }

    TableManager -- Table

```

### リレーション

```mermaid
classDiagram
    direction LR

    class EntityInfo {
        <<BaseSchema>>
        +schema_name : str
        +table_name : str
    }

    class BindColumn {
        <<BaseSchema>>
        +source_column : str
        +target_column : str
    }

    class Relation {
        <<BaseSchema>>
        +target : EntityInfo
        +bind_columns : list[BindColumn]
        +cardinarity_source : str = "1"
        +cardinarity_target : str = "1"
        +constraint_name : str | None = None
        +on_delete : str = "RESTRICT"
        +on_update : str = "RESTRICT"
        +deferrable : bool = False
        +initially_deferred : bool = False
        +match_type : str = "SIMPLE"
        +relationship_type : str = "association"
        +description : str | None = None
        +notes_ : list[Note]

        +@ notes() NoteManager
    }

    Relation -- EntityInfo : target
    Relation -- BindColumn : bind_columns
    Relation -- NoteManager : notes

    class RelationManager {
        -relations : list[Relation]

        +\_\_init__(relations: list[Relation])
        +\_\_getitem__(index: int) Relation
        +\_\_iter__() Generic~Relation~
        +\_\_len__() int

        +append(relation: Relation)
        +remove(relation: Relation)
    }

    RelationManager -- Relation

```

### ビュー

```mermaid
classDiagram
    direction LR

    class ViewColumn {
        +column_name : str
        +display_name : str
        +column_type : str
        +nullable : bool
        +source_table : str | None = None
        +source_column : str | None = None
        +is_computed : bool = False
    }

    class View {
        +view_name : str
        +display_name : str
        +select_statement : str
        +notes_ : list[Note]

        +@ notes() NoteManager
    }

    View -- ViewColumn
    View -- NoteManager : notes

    class ViewManager {
        -views : dict[str, View]

        +\_\_init__(views: dict[str, View])
        +\_\_getitem__(view_name: str) View
        +\_\_iter__() Generic~View~
        +\_\_len__() int
        +\_\_contains__(view_name: str) bool

        +append(view: View)
        +remove(view_name: str)
    }

    ViewManager -- View

```

### トリガー

```mermaid
classDiagram
    direction LR

    class Trigger {
        <<BaseSchema>>
        +trigger_name : str
        +display_name : str
        +table_name : str
        +timing : str
        +event : str
        +condition : str | None = None
        +body : str
        +notes_ : list[Note]

        +@ notes() NoteManager
    }

    Trigger -- NoteManager : notes

    class TriggerManager {
        -triggers : dict[str, Trigger]

        +\_\_init__(triggers: dict[str, Trigger])
        +\_\_getitem__(trigger_name: str) Trigger
        +\_\_iter__() Generic~Trigger~
        +\_\_len__() int
        +\_\_contains__(trigger_name: str) bool

        +append(trigger: Trigger)
        +remove(trigger_name: str)
    }

    TriggerManager -- Trigger
````

## サンプル

```yaml
schemas:
  main:
    tables:
      table_name:
        # テーブル定義
    views:
      view_name:
        # ビュー定義
    triggers:
      trigger_name:
        # トリガー定義
```

## ノートおよびメタデータ管理

- スキーマ定義に関連するノートやメタデータを管理するためのクラスを提供します。
- ノートは、スキーマの各要素に関連するメモや説明を保持し、メタデータは視覚情報を管理します。


### ノート

```mermaid
classDiagram
    direction LR

    class Note {
        <<BaseSchema>>
        +title : str
        +content : str
        +checked : bool = False
    }

    class NoteManager {
        -notes : list[Note]

        +__init__(notes: list[Note])
        +__getitem__(index: int) Note
        +__iter__() Generic~Note~
        +__len__() int

        +append(note: Note)
        +remove(note: Note)
    }

    NoteManager -- Note
```

### メタデータ

```mermaid
classDiagram
    direction LR

    class MetaData {
        <<BaseSchema>>
        +name : str
        +value: str | None = None
        +description : str | None = None
    }

    class MetaDataManager {
        -metadata : dict[str, MetaData]

        +__init__(metadata: list[MetaData])
        +__getitem__(key: str) MetaData
        +__iter__() Generic~MetaData~
        +__len__() int
        +__contains__(key: str) bool

        +append(metadata: MetaData)
        +remove(metadata: MetaData)
    }

    MetaDataManager -- MetaData

```
