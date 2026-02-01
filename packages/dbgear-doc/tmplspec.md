# DBGear Doc テンプレート仕様

本ドキュメントでは、`dbgear doc` コマンドで使用されるJinja2テンプレートに渡される変数について説明します。

## コマンド概要

```bash
dbgear doc --template <テンプレートファイル> -o <出力先> [--scope schema|table|view|trigger|procedure]
```

| オプション | 必須 | 説明 |
|-----------|------|------|
| `--template` | ○ | Jinja2テンプレートファイルのパス |
| `-o, --output` | ○ | 出力先（scope=schema: ファイルパス、その他: ディレクトリ） |
| `--scope` | - | データスコープ（デフォルト: `table`） |

**出力ファイルの拡張子**はテンプレートファイル名から自動決定されます:
- `template.md.j2` → `.md`
- `template.html.j2` → `.html`
- `template.yaml.j2` → `.yaml`

---

## scope='schema' の場合

スキーマ全体を1ファイルに出力します。`-o` で指定したパスがそのまま出力ファイルパスになります。

### テンプレート変数

| 変数名 | 型 | 説明 |
|--------|-----|------|
| `schemas` | `dict[str, Schema]` | スキーマ名をキー、Schemaオブジェクトを値とする辞書 |
| `registry` | `ColumnTypeRegistry` | カラム型レジストリ |
| `notes` | `NoteManager` | グローバルノートマネージャー |

### 使用例

```jinja2
schemas:
{% for schema_name, schema in schemas.items() | sort %}
  {{ schema_name }}:
    tables:
{% for table_name, table in schema.tables.tables.items() | sort %}
      - table_name: {{ table_name }}
        display_name: {{ table.display_name }}
{% endfor %}
{% endfor %}
```

### コマンド例

```bash
dbgear doc --template my_template.yaml.j2 --scope schema -o output.yaml
```

---

## scope='table' の場合（デフォルト）

テーブルごとに1ファイル出力します。`-o` で指定したディレクトリ配下に `{schema}/{table}.{ext}` 形式で出力されます。

### テンプレート変数

| 変数名 | 型 | 説明 |
|--------|-----|------|
| `schema_name` | `str` | スキーマ名 |
| `table_name` | `str` | テーブル名 |
| `table` | `Table` | テーブルオブジェクト |
| `referenced_by` | `list[dict]` | このテーブルを参照しているテーブル一覧（被参照テーブル） |

### `referenced_by` の構造

```python
{
    'table': Table,           # 参照元テーブルオブジェクト
    'relation': Relation,     # リレーションオブジェクト
}
```

テンプレートでは `ref.table.table_name`, `ref.table.display_name`, `ref.relation.constraint_name` などでアクセスできます。
詳細は下記の「Relation オブジェクト」セクションを参照してください。

### 使用例

```jinja2
# {{ table.display_name }} ({{ table_name }})

## Columns

| Column | Type | Nullable |
|--------|------|----------|
{% for col in table.columns %}
| {{ col.column_name }} | {{ col.column_type | format_column_type }} | {{ "YES" if col.nullable else "NO" }} |
{% endfor %}

{% if referenced_by %}
## Referenced By
{% for ref in referenced_by %}
- {{ ref.table.table_name }} ({{ ref.relation.constraint_name }})
{% endfor %}
{% endif %}
```

### コマンド例

```bash
dbgear doc --template table.md.j2 -o docs/
# 出力: docs/main/users.md, docs/main/orders.md, ...
```

---

## scope='view' の場合

ビューごとに1ファイル出力します。`-o` で指定したディレクトリ配下に `{schema}/{view}.{ext}` 形式で出力されます。

### テンプレート変数

| 変数名 | 型 | 説明 |
|--------|-----|------|
| `schema_name` | `str` | スキーマ名 |
| `view_name` | `str` | ビュー名 |
| `view` | `View` | ビューオブジェクト |

### 使用例

```jinja2
# {{ view.display_name }} ({{ view_name }})

Schema: {{ schema_name }}

## SELECT Statement

```sql
{{ view.select_statement }}
```
```

### コマンド例

```bash
dbgear doc --template view.md.j2 --scope view -o docs/
# 出力: docs/main/active_users.md, ...
```

---

## scope='trigger' の場合

トリガーごとに1ファイル出力します。`-o` で指定したディレクトリ配下に `{schema}/{trigger}.{ext}` 形式で出力されます。

### テンプレート変数

| 変数名 | 型 | 説明 |
|--------|-----|------|
| `schema_name` | `str` | スキーマ名 |
| `trigger_name` | `str` | トリガー名 |
| `trigger` | `Trigger` | トリガーオブジェクト |
| `target_table` | `Table \| None` | 対象テーブルオブジェクト（存在する場合） |

### 使用例

```jinja2
# {{ trigger.display_name }} ({{ trigger_name }})

- **Target Table**: {{ trigger.table_name }}
- **Timing**: {{ trigger.timing }}
- **Event**: {{ trigger.event }}

## Body

```sql
{{ trigger.body }}
```

{% if target_table %}
## Target Table Columns
{% for col in target_table.columns %}
- {{ col.column_name }}: {{ col.column_type | format_column_type }}
{% endfor %}
{% endif %}
```

### コマンド例

```bash
dbgear doc --template trigger.md.j2 --scope trigger -o docs/
# 出力: docs/main/update_timestamp.md, ...
```

---

## scope='procedure' の場合

プロシージャごとに1ファイル出力します。`-o` で指定したディレクトリ配下に `{schema}/{procedure}.{ext}` 形式で出力されます。

### テンプレート変数

| 変数名 | 型 | 説明 |
|--------|-----|------|
| `schema_name` | `str` | スキーマ名 |
| `procedure_name` | `str` | プロシージャ名 |
| `procedure` | `Procedure` | プロシージャオブジェクト |

### 使用例

```jinja2
# {{ procedure.display_name }} ({{ procedure_name }})

{% if procedure.is_function %}
**Type**: Function (returns {{ procedure.return_type }})
{% else %}
**Type**: Procedure
{% endif %}

## Parameters

{% for param in procedure.parameters %}
- {{ param.name }} ({{ param.mode }}): {{ param.data_type }}
{% endfor %}

## Body

```sql
{{ procedure.body }}
```
```

### コマンド例

```bash
dbgear doc --template procedure.md.j2 --scope procedure -o docs/
# 出力: docs/main/calculate_total.md, ...
```

---

## カスタムフィルター

テンプレートで使用可能なカスタムフィルター。

| フィルター名 | 説明 | 使用例 |
|-------------|------|--------|
| `get_table_note` | テーブルからノートテキストを取得 | `{{ table \| get_table_note }}` |
| `get_column_note` | カラムからノートテキストを取得 | `{{ col \| get_column_note }}` |
| `truncate_note` | テキストを指定長で切り詰め | `{{ text \| truncate_note(50) }}` |
| `escape_pipe` | パイプ文字をエスケープ | `{{ text \| escape_pipe }}` |
| `format_column_type` | カラム型を文字列に変換 | `{{ col.column_type \| format_column_type }}` |

---

## モデルオブジェクト参照

### Table オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `table_name` | `str` | テーブル名 |
| `display_name` | `str` | 表示名 |
| `columns` | `ColumnManager` | カラムマネージャー（イテレート可能） |
| `indexes` | `IndexManager` | インデックスマネージャー |
| `relations` | `RelationManager` | リレーションマネージャー |
| `notes` | `NoteManager` | ノートマネージャー |
| `categories` | `list[str]` | カテゴリリスト |
| `mysql_options` | `MySQLTableOptions \| None` | MySQL固有オプション |

### Column オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `column_name` | `str` | カラム名 |
| `display_name` | `str` | 表示名 |
| `column_type` | `ColumnType` | カラム型オブジェクト |
| `nullable` | `bool` | NULL許可 |
| `primary_key` | `int \| None` | 主キー順序（1始まり） |
| `default_value` | `str \| None` | デフォルト値 |
| `auto_increment` | `bool` | AUTO_INCREMENT |
| `notes` | `NoteManager` | ノートマネージャー |

### ColumnType オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `column_type` | `str` | 型定義文字列（例: `VARCHAR(100)`） |
| `base_type` | `str` | 基本型（例: `VARCHAR`） |

### View オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `view_name` | `str` | ビュー名 |
| `display_name` | `str` | 表示名 |
| `select_statement` | `str` | SELECT文 |
| `notes` | `NoteManager` | ノートマネージャー |

### Trigger オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `trigger_name` | `str` | トリガー名 |
| `display_name` | `str` | 表示名 |
| `table_name` | `str` | 対象テーブル名 |
| `timing` | `str` | タイミング（BEFORE / AFTER / INSTEAD OF） |
| `event` | `str` | イベント（INSERT / UPDATE / DELETE） |
| `condition` | `str \| None` | WHEN条件（オプション） |
| `body` | `str` | トリガー本体 |
| `notes` | `NoteManager` | ノートマネージャー |

### Procedure オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `procedure_name` | `str` | プロシージャ名 |
| `display_name` | `str` | 表示名 |
| `parameters` | `list[ProcedureParameter]` | パラメータリスト |
| `return_type` | `str \| None` | 戻り値型（関数の場合） |
| `body` | `str` | プロシージャ本体 |
| `language` | `str` | 言語（SQL, PLPGSQL等） |
| `deterministic` | `bool` | 決定的かどうか |
| `is_function` | `bool` | 関数かどうか（プロパティ） |
| `notes` | `NoteManager` | ノートマネージャー |

### ProcedureParameter オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `name` | `str` | パラメータ名 |
| `mode` | `str` | モード（IN / OUT / INOUT） |
| `data_type` | `str` | データ型 |

### Schema オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `name` | `str` | スキーマ名 |
| `tables` | `TableManager` | テーブルマネージャー |
| `views` | `ViewManager` | ビューマネージャー |
| `triggers` | `TriggerManager` | トリガーマネージャー |
| `procedures` | `ProcedureManager` | プロシージャマネージャー |
| `notes` | `NoteManager` | ノートマネージャー |

**Manager からエンティティ辞書を取得:**
```jinja2
{% for table_name, table in schema.tables.tables.items() %}
{% for view_name, view in schema.views.views.items() %}
{% for trigger_name, trigger in schema.triggers.triggers.items() %}
{% for procedure_name, procedure in schema.procedures.procedures.items() %}
```

### Index オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `index_name` | `str \| None` | インデックス名 |
| `columns` | `list[str]` | カラム名リスト |
| `unique` | `bool` | ユニーク制約 |

### Relation オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `target` | `EntityInfo` | 参照先テーブル情報 |
| `bind_columns` | `list[BindColumn]` | カラムバインディングリスト |
| `constraint_name` | `str \| None` | FK制約名 |
| `on_delete` | `str` | ON DELETE アクション |
| `on_update` | `str` | ON UPDATE アクション |

### BindColumn オブジェクト

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `source_column` | `str` | ソース側カラム名 |
| `target_column` | `str` | ターゲット側カラム名 |

### ColumnTypeRegistry オブジェクト

カスタムカラム型の辞書。イテレート可能、キーアクセス可能。

| プロパティ/メソッド | 型 | 説明 |
|-------------------|-----|------|
| `types` | `dict[str, ColumnType]` | 型名をキー、ColumnTypeを値とする辞書 |
| `registry[key]` | `ColumnType` | キーで型を取得 |

```jinja2
{% for col_type in registry %}
- {{ col_type.column_type }}
{% endfor %}
```
