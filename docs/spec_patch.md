# パッチ機能仕様

## 概要

パッチ機能は、データベースのバックアップテーブルから特定条件に合致するデータのみを選択的に復元するための機能です。通常のデータ復元では全レコードが復元されますが、パッチ機能を使用することで必要なデータだけを抽出して復元できます。

## アーキテクチャ

### コンポーネント構成

```
packages/dbgear/dbgear/
├── patch.py              # パッチ設定の解析とSQL生成
├── operations.py         # パッチ実行ロジック（_execute_patch メソッド）
└── main.py              # CLIインターフェース（--patch オプション）
```

### 処理フロー

1. **パッチファイル読み込み**: YAML形式のパッチ設定ファイルを読み込み
2. **バリデーション**: パッチ設定の妥当性チェックとセキュリティ検証
3. **SQL生成**: バックアップテーブルからのSELECT + INSERT文を生成
4. **実行**: 生成されたSQLを実行してデータを復元

```
[パッチファイル.yaml]
        ↓
[PatchConfig.load_from_file()]
        ↓
[validate_patch_config()]
        ↓
[generate_patch_sql()]
        ↓
[engine.execute()]
```

## パッチファイル形式

### YAML構造

```yaml
name: テーブル名          # 対象テーブル名（必須）
columns:                 # カラムマッピング（必須）
  # キー: INSERT先のカラム名
  # 値: SELECT側の式（カラム名、SQL関数、固定値、計算式）
  col1: col1             # バックアップテーブルのカラムを直接指定
  col2: "NOW()"          # SQL関数
  col3: "'default'"      # 固定値（文字列リテラル）
  col4: "100"            # 固定値（数値）
  col5: "col1 * 1.1"     # 計算式
where: "WHERE条件"       # データを絞り込む条件（オプション）
```

### パラメータ詳細

#### name（必須）
- **型**: 文字列
- **説明**: 復元対象のテーブル名
- **検証**:
  - 空文字列不可
  - `--target` オプションで指定したテーブル名と一致必須

#### columns（必須）
- **型**: ディクショナリ（キー: 文字列、値: 文字列）
- **説明**: INSERT先のカラム名とSELECT側の式のマッピング
- **検証**:
  - 空のディクショナリ不可
  - 1つ以上のカラムマッピングが必要
  - キーと値は両方とも文字列型である必要がある
- **キー（INSERT先カラム名）**:
  - 復元先テーブルに存在するカラム名を指定
  - 存在しないカラム名を指定するとSQL実行時にエラー
- **値（SELECT式）**:
  - **カラム名**: バックアップテーブルのカラムを直接指定（例: `col_id`）
  - **SQL関数**: MySQL組み込み関数（例: `NOW()`, `UUID()`, `CURRENT_TIMESTAMP`）
  - **固定値（文字列）**: シングルクォートで囲む（例: `'active'`, `'system'`）
  - **固定値（数値）**: そのまま記述（例: `100`, `0`, `1.5`）
  - **計算式**: 四則演算など（例: `num * 1.1`, `price * quantity`）
  - **CASE文**: 条件分岐（例: `CASE WHEN num > 100 THEN 'large' ELSE 'small' END`）
  - **サブクエリ**: SELECTサブクエリ（例: `(SELECT MAX(id) FROM other_table)`）

#### where（オプション）
- **型**: 文字列
- **説明**: データを絞り込むためのWHERE条件
- **検証**:
  - SQLインジェクション対策として危険なパターンを検出
  - 省略時は全レコードが対象
- **制限事項**:
  - 以下のパターンが含まれているとエラー
    - `;` (複数SQL文の実行防止)
    - `--` (コメント注入防止)
    - `/*`, `*/` (コメント注入防止)
    - `DROP`, `DELETE`, `UPDATE` (破壊的操作の防止)

## 生成されるSQL

### SQL構造

```sql
INSERT INTO {env}.{table_name}
SELECT
  {select_column1},
  {select_column2},
  {select_column3}
FROM {env}.bak_{table_name}_{backup_key}
WHERE {where_clause}
```

### パラメータ展開例

**パッチファイル:**
```yaml
name: users
columns:
  id: id
  username: username
  email: email
  status: "'active'"
  created_at: "NOW()"
where: "created_at >= '2025-01-01'"
```

**生成されるSQL:**
```sql
INSERT INTO production.users (
  id,
  username,
  email,
  status,
  created_at
)
SELECT
  id,
  username,
  email,
  'active',
  NOW()
FROM production.bak_users_20251210120000
WHERE created_at >= '2025-01-01'
```

## 使用方法

### CLIコマンド

```bash
dbgear apply <deployment> <environment> --target <table_name> --patch <patch_file>
```

**必須オプション:**
- `--target`: 対象テーブル名
- `--patch`: パッチファイルのパス

**使用例:**
```bash
# 基本的な使い方
dbgear apply localhost development --target users --patch users.patch.yaml

# 絶対パスでパッチファイルを指定
dbgear apply localhost development --target orders --patch /path/to/orders.patch.yaml
```

### プログラムでの利用

```python
from dbgear.patch import PatchConfig, generate_patch_sql, validate_patch_config

# パッチ設定を読み込み
patch_config = PatchConfig.load_from_file('users.patch.yaml')

# バリデーション
errors = validate_patch_config(patch_config)
if errors:
    print(f"Validation errors: {errors}")
    exit(1)

# SQL生成
sql = generate_patch_sql('production', patch_config, '20251210120000')
print(sql)

# SQLを実行
from dbgear.dbio import engine
engine.execute(conn, sql)
```

## datamodelとの関係

パッチ機能は、datamodel（データモデル定義ファイル）の有無によって動作が異なります。

### datamodelが存在する場合

datamodelの`sync_mode`設定と組み合わせて動作します：

- **`sync_mode: drop_create`**:
  - 初期データ投入のみ実行
  - リストア処理はスキップ（patchも実行されない）

- **`sync_mode: manual`**:
  - `--all`指定時：スキップ（データ依存/トリガー問題を回避）
  - `--target`個別指定時：初期データ投入後、以下のいずれかを実行
    - `--patch`オプション指定時：patchファイルによる選択的復元
    - 上記以外：バックアップから新規レコードのみ追加（INSERT IGNORE）

- **`sync_mode: update_diff`**:
  - `--all`指定時も復元実行
  - 初期データ投入後、以下のいずれかを実行：
    - `--patch`オプション指定時：patchファイルによる選択的復元
    - 上記以外：バックアップから新規レコードのみ追加（INSERT IGNORE）

- **`sync_mode: replace`**:
  - `--all`指定時も復元実行
  - 初期データ投入後、以下のいずれかを実行：
    - `--patch`オプション指定時：patchファイルによる選択的復元
    - 上記以外：バックアップで既存レコードを上書き（REPLACE INTO）

**datamodelの例:**
```yaml
# env1/sample/main@users.yaml
description: "ユーザーテーブル"
sync_mode: manual  # リストア処理を有効化
data_type: yaml
```

### datamodelが存在しない場合

**v0.35.0以降**: datamodelがなくてもpatch機能およびバックアップ復元を使用可能

```bash
# datamodelなしでpatchファイルを適用
dbgear apply localhost development --target users --patch users.patch.yaml

# datamodelなしでバックアップから全件復元
dbgear apply localhost development --target users --restore-backup
```

**動作条件**:
- `--target`オプションでテーブル名を指定
- `--patch`または`--restore-backup`オプションを指定
- 対象テーブルのバックアップテーブル（`bak_{table_name}_{timestamp}`）が存在すること

**メリット**:
- 初期データ定義が不要なテーブルでもバックアップ復元が可能
- 一時的なデータ復元操作が簡潔に実行できる
- スキーマ定義のみでデータ管理が完結する場合に便利

**注意**: datamodelが定義されている場合は、datamodelの`sync_mode`設定が優先されます。

## サンプルファイル

### 基本サンプル

#### 1. 特定ユーザーのデータのみ復元

**ファイル**: `etc/test/env1/sample2/main@test_table.patch.yaml`

```yaml
name: test_table
columns:
  col_id: col_id
  name: name
  test_18n: test_18n
  num: num
  update_date: update_date
  update_user: update_user
where: "update_user = 'admin'"
```

#### 2. 直近30日のデータのみ復元

**ファイル**: `etc/test/env1/sample2/main@test_table_recent.patch.yaml`

```yaml
name: test_table
columns:
  col_id: col_id
  name: name
  test_18n: test_18n
  num: num
  update_date: update_date
  update_user: update_user
where: "update_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
```

#### 3. 数値条件でフィルタ

**ファイル**: `etc/test/env1/sample2/main@test_table_numeric.patch.yaml`

```yaml
name: test_table
columns:
  col_id: col_id
  name: name
  test_18n: test_18n
  num: num
  update_date: update_date
  update_user: update_user
where: "num >= 100"
```

#### 4. 全データ復元（WHERE条件なし）

**ファイル**: `etc/test/env1/sample2/main@test_table_all.patch.yaml`

```yaml
name: test_table
columns:
  col_id: col_id
  name: name
  test_18n: test_18n
  num: num
  update_date: update_date
  update_user: update_user
# where句を省略すると全データが対象
```

#### 5. 親テーブルとの関連を考慮

**ファイル**: `etc/test/env1/sample2/main@tbl_child.patch.yaml`

```yaml
name: tbl_child
columns:
  child_id: child_id
  col_id: col_id
  name: name
  update_date: update_date
  update_user: update_user
where: "col_id IN (SELECT col_id FROM testdb1.bak_test_table_20251210000000 WHERE update_user = 'admin')"
```

### 高度なサンプル

#### 6. SQL関数と計算式を使用

**ファイル**: `etc/test/env1/sample2/main@test_table_advanced.patch.yaml`

```yaml
name: test_table
columns:
  col_id: col_id
  name: name
  test_18n: test_18n
  num: "num * 1.1"                    # 計算式: 10%増加
  update_date: "NOW()"                # SQL関数: 現在時刻
  update_user: "'migration_script'"   # 固定値: 文字列
where: "update_user = 'admin'"
```

#### 7. 新カラムにデフォルト値設定

**ファイル**: `etc/test/env1/sample2/main@test_table_with_defaults.patch.yaml`

```yaml
name: test_table
columns:
  # 既存カラム
  col_id: col_id
  name: name
  test_18n: test_18n
  num: num

  # 新しく追加されたカラムにデフォルト値を設定
  status: "'active'"              # 固定値
  priority: "100"                 # 固定値（数値）
  uuid: "UUID()"                  # UUID生成
  created_at: "CURRENT_TIMESTAMP" # タイムスタンプ
  update_date: "NOW()"
  update_user: "'system'"
```

#### 8. CASE文によるデータ変換

**ファイル**: `etc/test/env1/sample2/main@test_table_transform.patch.yaml`

```yaml
name: test_table
columns:
  col_id: col_id
  name: name
  # JSONカラムは除外（個人情報削除）
  status: "CASE WHEN num >= 100 THEN 'high' WHEN num >= 50 THEN 'medium' ELSE 'low' END"
  num: "num * 2"                      # 計算式
  update_date: "NOW()"
  update_user: "'data_migration'"
where: "num IS NOT NULL"
```

## ユースケース

### 1. 本番環境へのマイグレーション

**課題**: テストデータを除外して本番データのみを移行したい

**解決策**:
```yaml
name: users
select:
  - user_id
  - username
  - email
where: "environment = 'production'"
```

### 2. 個人情報のサニタイゼーション

**課題**: 特定カラムを除外してデータを復元したい

**解決策**:
```yaml
name: users
columns:
  user_id: user_id
  username: username
  # emailやphone_numberなどの個人情報カラムは除外
  created_at: created_at
# where条件なし = 全レコード対象
```

### 3. 時系列データの部分復元

**課題**: ディスク容量を節約するため、直近のデータのみ復元したい

**解決策**:
```yaml
name: access_logs
columns:
  log_id: log_id
  user_id: user_id
  access_time: access_time
  url: url
where: "access_time >= DATE_SUB(NOW(), INTERVAL 90 DAY)"
```

### 4. 条件付きロールバック

**課題**: 特定条件のデータのみを以前の状態に戻したい

**解決策**:
```yaml
name: products
columns:
  product_id: product_id
  product_name: product_name
  price: price
  stock: stock
where: "category = 'electronics' AND updated_at >= '2025-12-01'"
```

### 5. スキーマ変更時の新カラムへのデフォルト値設定

**課題**: テーブルに新しいカラムが追加されたが、バックアップテーブルには存在しない

**解決策**:
```yaml
name: orders
columns:
  order_id: order_id
  customer_id: customer_id
  total_amount: total_amount
  order_date: order_date
  # 新しく追加されたカラムにデフォルト値を設定
  status: "'pending'"
  priority: "1"
  created_at: "NOW()"
  created_by: "'migration_script'"
```

### 6. データ変換・正規化

**課題**: データ形式を変更しながら復元したい

**解決策**:
```yaml
name: products
columns:
  product_id: product_id
  product_name: product_name
  price: price
  # 税込価格を計算
  price_with_tax: "price * 1.1"
  # ステータスコードを文字列に変換
  status: "CASE WHEN status_code = 1 THEN 'active' WHEN status_code = 2 THEN 'inactive' ELSE 'unknown' END"
  updated_at: "NOW()"
```

### 7. 監査情報の自動追加

**課題**: マイグレーション履歴を記録するためのカラムを追加したい

**解決策**:
```yaml
name: users
columns:
  user_id: user_id
  username: username
  email: email
  # 監査情報を自動追加
  migrated_at: "NOW()"
  migrated_by: "'admin'"
  migration_version: "'v2.0'"
  migration_batch: "UUID()"
```

## セキュリティ機能

### バリデーション機能

パッチファイルには自動バリデーションが組み込まれており、以下の観点でチェックを実行します：

#### 1. 必須項目チェック
- `name` が空でないこと
- `select` が空リストでないこと

#### 2. SQLインジェクション対策

**検出パターン**:
- `;` → 複数SQL文の実行防止
- `--` → SQLコメント注入防止
- `/*`, `*/` → ブロックコメント注入防止
- `DROP` → テーブル削除防止
- `DELETE` → データ削除防止
- `UPDATE` → データ更新防止

**検出時の動作**:
```python
errors = validate_patch_config(patch_config)
# エラー例: ["Potentially dangerous pattern ';' found in WHERE clause"]
```

#### 3. テーブル名の一致チェック

パッチファイルの `name` と `--target` オプションで指定したテーブル名が一致しているかをチェックします。

```python
if patch_config.name != table_name:
    raise ValueError(f"Patch table name '{patch_config.name}' does not match target '{table_name}'")
```

## 実装クラス・関数

### PatchConfig クラス

**場所**: `packages/dbgear/dbgear/patch.py:14-48`

```python
class PatchConfig:
    """Represents a patch configuration loaded from YAML."""

    def __init__(self, name: str, columns: Dict[str, str], where: Optional[str] = None)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PatchConfig'

    @classmethod
    def load_from_file(cls, file_path: str) -> 'PatchConfig'
```

**属性**:
- `name: str` - 対象テーブル名
- `columns: Dict[str, str]` - カラムマッピング（INSERT先カラム名 → SELECT式）
- `where: Optional[str]` - WHERE条件

### generate_patch_sql 関数

**場所**: `packages/dbgear/dbgear/patch.py:52-86`

```python
def generate_patch_sql(env: str, patch_config: PatchConfig, backup_key: str) -> str:
    """
    Generate INSERT SQL from patch configuration.

    Args:
        env: Database environment name
        patch_config: Patch configuration
        backup_key: Backup table timestamp key (YYYYMMDDHHMMSS)

    Returns:
        Generated INSERT SQL string
    """
```

**処理内容**:
1. INSERT先のカラム名リストを生成（`columns.keys()`）
2. SELECT側の式リストを生成（`columns.values()`）
3. WHERE句を構築（指定されている場合）
4. 完全なINSERT...SELECT文を生成

### validate_patch_config 関数

**場所**: `packages/dbgear/dbgear/patch.py:89-129`

```python
def validate_patch_config(patch_config: PatchConfig) -> List[str]:
    """
    Validate patch configuration and return list of warnings/errors.

    Returns:
        List of validation messages (empty if valid)
    """
```

**検証内容**:
1. テーブル名が空でないことを確認
2. カラムマッピングが空でないことを確認
3. WHERE句に危険なパターンがないか確認（`;`, `--`, `/*`, `*/`, `DROP`, `DELETE`, `UPDATE`）
4. 各カラム式に危険なパターンがないか確認（`;`, `--`, `/*`, `*/`）
5. カラム名と式の型が文字列であることを確認

### Operation._execute_patch メソッド

**場所**: `packages/dbgear/dbgear/operations.py:177-205`

```python
def _execute_patch(self, env: str, table_name: str, patch_file: str):
    """Execute patch file for data restoration."""
```

## 制限事項

### 1. バックアップテーブルの存在

パッチ機能を使用するには、対象テーブルのバックアップテーブル（`bak_テーブル名_YYYYMMDDHHMMSS`）が存在している必要があります。

### 2. テーブル名の一致

`--target` オプションで指定するテーブル名とパッチファイルの `name` が一致している必要があります。

### 3. カラムの存在確認

`columns` のキー（INSERT先カラム名）は、実際のテーブル定義に存在している必要があります。存在しないカラム名を指定するとSQL実行時にエラーになります。

`columns` の値（SELECT式）でバックアップテーブルのカラムを参照する場合、そのカラムがバックアップテーブルに存在している必要があります。

### 4. WHERE条件の制限

WHERE条件には以下の文字列が含まれているとエラーになります：
- `;`, `--`, `/*`, `*/`, `DROP`, `DELETE`, `UPDATE`

### 5. 単一テーブルのみ対象

パッチファイルは1つのテーブルにのみ適用されます。複数のテーブルに対してパッチを適用する場合は、テーブルごとにパッチファイルを作成し、個別に実行する必要があります。

## エラーハンドリング

### パッチファイル読み込みエラー

```python
try:
    patch_config = PatchConfig.load_from_file(patch_file)
except FileNotFoundError:
    # ファイルが見つからない
    raise ValueError(f"Patch file not found: {patch_file}")
except yaml.YAMLError as e:
    # YAML形式が不正
    raise ValueError(f"Invalid YAML in patch file: {e}")
```

### バリデーションエラー

```python
errors = validate_patch_config(patch_config)
if errors:
    for error in errors:
        logger.error(f"Patch validation error: {error}")
    raise ValueError(f"Invalid patch configuration: {errors[0]}")
```

### テーブル名不一致エラー

```python
if patch_config.name != table_name:
    raise ValueError(
        f"Patch table name '{patch_config.name}' does not match target '{table_name}'"
    )
```

### SQL実行エラー

```python
try:
    engine.execute(self.conn, sql)
except Exception as e:
    logger.error(f"Failed to execute patch {patch_file}: {e}")
    raise
```

## ログ出力

### 正常系ログ

```
INFO: executing patch users.patch.yaml for production.users
DEBUG: patch SQL: INSERT INTO production.users SELECT ...
```

### エラー系ログ

```
ERROR: Patch validation error: Potentially dangerous pattern ';' found in WHERE clause
ERROR: Failed to execute patch users.patch.yaml: Table 'bak_users_20251210000000' doesn't exist
```

## 関連仕様

- [データモデル仕様](spec_datamodel.md) - データモデルの同期モードとの関係
- [マッピング仕様](spec_mapping.md) - 環境とインスタンスのマッピング
- [プロジェクト仕様](spec_project.md) - プロジェクト設定とデプロイメント

## 今後の拡張案

### 1. 複数テーブルのバッチ適用

複数のパッチファイルをまとめて適用する機能。

```bash
dbgear apply localhost development --patch-dir patches/
```

### 2. パッチファイルのテンプレート機能

パラメータを外部から注入できるテンプレート機能。

```yaml
name: users
columns:
  user_id: user_id
  username: username
  status: "'{{ default_status }}'"
where: "created_at >= '{{ start_date }}'"
```

### 3. ドライランモード

実際にSQLを実行せず、生成されるSQLを確認するモード。

```bash
dbgear apply localhost development --target users --patch users.patch.yaml --dry-run
```

### 4. パッチ適用履歴の記録

どのパッチがいつ適用されたかを記録する機能。

```sql
CREATE TABLE patch_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255),
    patch_file VARCHAR(255),
    applied_at TIMESTAMP,
    record_count INT
);
```
