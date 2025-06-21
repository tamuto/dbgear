# DBGear 機能拡張ロードマップ

DBGearの将来的な機能拡張計画と実装指針をまとめたドキュメントです。

## 🎯 計画中の機能拡張

### 1. UI フレームワーク変更 (Material-UI → Shadcn/UI)

**目的**: モダンなデザインシステムへの移行とバンドルサイズの最適化

**影響範囲**: 
- フロントエンド全体のリファクタリング
- 全コンポーネントの再実装
- テーマシステムの変更

**実装ステップ**:
```bash
# Phase 1: 環境準備
- Shadcn/UI のセットアップ
- Tailwind CSS の導入
- 既存のMaterial-UIとの共存環境構築

# Phase 2: コアコンポーネント移行
- BaseLayout.tsx の変更
- 基本的なUIコンポーネント (Button, Input, Dialog) の移行
- テーマシステムの実装

# Phase 3: 機能コンポーネント移行
- DataEditor.tsx の移行
- DataSettings.tsx の移行
- ChatBox.tsx の移行

# Phase 4: 最終調整
- Material-UI の完全削除
- スタイリングの統一
- レスポンシブ対応の確認
```

**技術的考慮事項**:
- TypeScript型定義の更新
- i18next との統合
- アクセシビリティの維持
- パフォーマンスの最適化

**リスク**:
- 大規模なUIの変更によるユーザビリティへの影響
- 既存機能の動作確認が必要

---

### 2. 内蔵スキーマバージョン管理システム

**目的**: 外部ツール（A5:SQL Mk-2等）に依存しない独自のスキーマ管理機能

**現在の課題**:
- A5:SQL Mk-2 ファイルへの依存
- スキーマ変更の追跡が困難
- マイグレーション機能の不足

**新機能設計**:
```yaml
# schema.yaml (新フォーマット)
version: "1.2.0"
schemas:
  main:
    tables:
      users:
        version: "1.1.0"
        fields:
          id:
            type: bigint
            primary_key: true
            auto_increment: true
          name:
            type: varchar(255)
            not_null: true
          created_at:
            type: datetime
            default: CURRENT_TIMESTAMP
        indexes:
          - name: idx_name
            fields: [name]
            unique: true
migrations:
  - version: "1.1.0"
    description: "Add user name unique index"
    up: |
      ALTER TABLE users ADD UNIQUE INDEX idx_name (name);
    down: |
      ALTER TABLE users DROP INDEX idx_name;
```

**実装ステップ**:
```bash
# Phase 1: スキーマ定義システム
- dbgear/definitions/internal_schema.py の実装
- YAML形式でのスキーマ定義パーサー
- 既存スキーマからの変換機能

# Phase 2: バージョン管理機能
- dbgear/versioning/ モジュールの追加
- マイグレーション生成機能
- スキーマ差分検出機能

# Phase 3: Web UI対応 ✅ 完了
- ✅ スキーマエディター機能 (Schema Management API実装完了)
  - スキーマ作成・削除・更新
  - テーブル定義のCRUD操作
  - フィールド管理 (カラム定義の作成・編集・削除)
  - インデックス管理 (自動命名対応)
  - ビュー管理 (データベースビューの定義・編集)
  - スキーマ検証 (テーブル・フィールド・外部キー制約の検証)
- 🔄 マイグレーション管理画面 (未実装)
- 🔄 バージョン履歴表示 (未実装)

# Phase 4: CLI拡張
- dbgear schema コマンド群の追加
- マイグレーション実行機能
```

**新CLI コマンド**:
```bash
# スキーマ管理
dbgear schema init                    # 新規スキーマ作成
dbgear schema diff                    # スキーマ差分表示
dbgear schema migrate                 # マイグレーション実行
dbgear schema rollback               # ロールバック実行
dbgear schema export --format a5er   # 外部形式でエクスポート
```

---

### 3. ドキュメント生成機能

**目的**: スキーマ定義からER図とテーブル定義書の自動生成

**出力形式**:
- ER図: SVG, PNG, PDF
- テーブル定義書: HTML, PDF, Markdown

**実装アーキテクチャ**:
```python
# dbgear/docs/ モジュール
dbgear/
  docs/
    __init__.py
    generators/
      __init__.py
      er_diagram.py      # Graphviz/D2を使用
      table_spec.py      # HTMLテンプレート生成
      base.py           # 共通基底クラス
    templates/
      table_spec.html    # Jinja2テンプレート
      er_diagram.d2     # D2テンプレート
    exporters/
      __init__.py
      pdf.py            # WeasyPrintを使用
      svg.py
```

**実装ステップ**:
```bash
# Phase 1: ER図生成
- D2 または Graphviz による図表生成
- テーブル関連の可視化
- Web UI での図表表示

# Phase 2: テーブル定義書生成
- HTMLテンプレートによる定義書生成
- PDF出力機能
- カスタムテンプレート対応

# Phase 3: CLI統合
- dbgear docs コマンドの追加
- 出力形式の選択機能
```

**新CLI コマンド**:
```bash
dbgear docs er --output diagram.svg         # ER図生成
dbgear docs tables --format pdf             # テーブル定義書生成
dbgear docs all --output-dir ./docs         # 全ドキュメント生成
```

**依存関係**:
- D2 or Graphviz (ER図生成)
- Jinja2 (テンプレートエンジン)
- WeasyPrint (PDF生成)

---

### 4. MCP サーバー化

**目的**: LLM から DBGear を直接操作可能にする

**MCPサーバー機能**:
- プロジェクト情報の取得
- データの読み書き
- スキーマ情報の提供
- マイグレーション実行

**実装アーキテクチャ**:
```python
# dbgear/mcp/ モジュール
dbgear/
  mcp/
    __init__.py
    server.py           # MCP server実装
    tools/
      __init__.py
      project.py        # プロジェクト操作
      data.py          # データ操作
      schema.py        # スキーマ操作
      migration.py     # マイグレーション操作
    schemas/
      __init__.py
      requests.py      # リクエストスキーマ
      responses.py     # レスポンススキーマ
```

**MCPツール定義**:
```json
{
  "tools": [
    {
      "name": "dbgear_get_project_info",
      "description": "プロジェクト情報を取得",
      "inputSchema": {
        "type": "object",
        "properties": {
          "project_path": {"type": "string"}
        }
      }
    },
    {
      "name": "dbgear_get_table_data",
      "description": "テーブルデータを取得",
      "inputSchema": {
        "type": "object",
        "properties": {
          "table_name": {"type": "string"},
          "environment": {"type": "string"}
        }
      }
    },
    {
      "name": "dbgear_update_table_data",
      "description": "テーブルデータを更新"
    },
    {
      "name": "dbgear_generate_migration",
      "description": "マイグレーションを生成"
    }
  ]
}
```

**実装ステップ**:
```bash
# Phase 1: MCP基盤
- MCPサーバーの基本実装
- 基本的なプロジェクト操作ツール

# Phase 2: データ操作機能
- データ読み取りツール
- データ更新ツール
- バリデーション機能

# Phase 3: 高度な機能
- スキーマ操作ツール
- マイグレーション機能
- ドキュメント生成連携
```

**新CLI コマンド**:
```bash
dbgear mcp start                    # MCPサーバー起動
dbgear mcp --port 3000             # ポート指定起動
```

---

### 5. ビュー管理機能の拡張

**目的**: 現在のシンプルなビュー定義から高度なSQL解析・依存関係管理への発展

**現在の実装状況**:
- ✅ 基本的なビュー定義 (YAML形式でSQL文のみ記述)
- ✅ データベースビューのCRUD操作
- ✅ 基本的な依存関係チェック機能
- ✅ テスト環境の整備 (19テストケース)

**将来の拡張機能**:

#### Phase 1: SQL解析エンジンの導入
```python
# dbgear/analysis/ モジュール
dbgear/
  analysis/
    __init__.py
    sql_parser.py       # sqlparseまたはpglast使用
    dependency_resolver.py  # 依存関係自動検出
    column_inference.py     # カラム定義自動推定
    validation.py          # 高度な検証機能
```

**機能詳細**:
```python
class SQLParser:
    def parse_view_dependencies(self, select_statement: str) -> list[str]:
        """FROM句、JOIN句からテーブル/ビュー依存関係を自動抽出"""
        
    def parse_view_columns(self, select_statement: str, schema_registry: dict) -> list[ViewColumn]:
        """SELECT句からカラム定義を自動生成（型情報は参照先から継承）"""
        
    def detect_circular_dependencies(self, views: dict[str, View]) -> list[str]:
        """循環依存を検出"""
        
    def validate_sql_syntax(self, select_statement: str, dialect: str = 'mysql') -> ValidationResult:
        """SQL文法チェック"""
```

#### Phase 2: 自動カラム定義生成
```yaml
# 現在: 手動でSQLのみ定義
views:
  user_summary:
    select_statement: |
      SELECT u.id, u.name, COUNT(o.id) as order_count
      FROM users u LEFT JOIN orders o ON u.id = o.user_id
      GROUP BY u.id, u.name

# 将来: 自動でカラム定義を生成
views:
  user_summary:
    select_statement: |
      SELECT u.id, u.name, COUNT(o.id) as order_count
      FROM users u LEFT JOIN orders o ON u.id = o.user_id
      GROUP BY u.id, u.name
    # 以下は自動生成される
    _auto_generated_columns:
      - column_name: id
        column_type: BIGINT
        nullable: false
        source_table: users
        source_column: id
      - column_name: name  
        column_type: VARCHAR(100)
        nullable: false
        source_table: users
        source_column: name
      - column_name: order_count
        column_type: BIGINT
        nullable: false
        is_computed: true
    _dependencies: [users, orders]
    _dependency_graph: 
      users: [id, name]
      orders: [id, user_id]
```

#### Phase 3: 高度な依存関係管理
```python
class ViewDependencyManager:
    def analyze_impact(self, table_name: str) -> ImpactAnalysis:
        """テーブル変更時の影響範囲を分析"""
        
    def suggest_view_updates(self, schema_changes: list[SchemaChange]) -> list[ViewUpdate]:
        """スキーマ変更に応じたビュー更新を提案"""
        
    def generate_view_creation_order(self, views: dict[str, View]) -> list[str]:
        """依存関係を考慮したビュー作成順序を生成"""
        
    def validate_view_consistency(self, views: dict[str, View]) -> ValidationResult:
        """ビュー間の整合性を検証"""
```

#### Phase 4: CLI機能拡張
```bash
# ビュー専用コマンド群
dbgear view list                           # ビュー一覧表示
dbgear view analyze user_summary           # 指定ビューの分析
dbgear view dependencies user_summary      # 依存関係表示
dbgear view impact users                   # テーブル変更の影響分析
dbgear view validate                       # 全ビューの整合性チェック
dbgear view refresh user_summary           # ビューの再作成
dbgear view graph --output deps.svg        # 依存関係グラフ生成
```

#### Phase 5: Web UI連携
- ビューエディター (SQL構文ハイライト、補完機能)
- 依存関係グラフの可視化
- ビュー作成ウィザード
- パフォーマンス分析機能

**技術的依存関係**:
- sqlparse or pglast (SQL解析)
- networkx (依存関係グラフ)
- graphviz (図表生成)

**実装ステップ**:
```bash
# Phase 1: SQL解析基盤 (2週間)
- sqlparseライブラリの統合
- 基本的な依存関係検出機能
- 単体テストの作成

# Phase 2: カラム推定機能 (2週間)  
- スキーマレジストリとの連携
- 型情報の自動推定
- エラーハンドリングの強化

# Phase 3: 高度な検証機能 (2週間)
- 循環依存検出
- 影響範囲分析
- パフォーマンス最適化

# Phase 4: CLI・Web UI統合 (2週間)
- 新コマンドの実装
- Web UIへの統合
- ドキュメント更新
```

**現在の設計との互換性**:
- 既存のView/ViewColumnクラスは維持
- `_parse_sql()` メソッドの実装を拡張
- 段階的な機能追加により後方互換性を保持

---

### 6. DB適用コマンドの拡充

**目的**: より安全で柔軟なデータベース操作機能

**新機能**:
- スキーマ整合性チェック
- データバックアップ機能強化
- ドライラン機能
- 部分適用機能

**拡張コマンド**:
```bash
# スキーマチェック
dbgear apply --dry-run localhost test        # 実際には実行しない
dbgear apply --check-only localhost test     # チェックのみ実行
dbgear apply --validate-schema localhost test # スキーマ検証

# バックアップ機能
dbgear backup create localhost test          # 手動バックアップ作成
dbgear backup restore localhost test --date 20240101  # バックアップ復元
dbgear backup list localhost test           # バックアップ一覧

# 部分適用
dbgear apply localhost test --tables user,order       # 特定テーブルのみ
dbgear apply localhost test --exclude-data           # スキーマのみ適用
dbgear apply localhost test --data-only              # データのみ適用

# 詳細オプション
dbgear apply localhost test --force          # 警告無視して実行
dbgear apply localhost test --verbose        # 詳細ログ出力
dbgear apply localhost test --parallel       # 並列実行
```

**実装ステップ**:
```bash
# Phase 1: チェック機能強化
- スキーマ整合性検証
- データ整合性検証
- 外部キー制約チェック

# Phase 2: バックアップ機能
- 自動バックアップ機能
- 世代管理機能
- 復元機能

# Phase 3: 高度な適用機能
- 部分適用機能
- 並列処理対応
- トランザクション管理強化
```

**アーキテクチャ変更**:
```python
# dbgear/operations.py の拡張
class AdvancedOperation(Operation):
    def validate_schema(self) -> ValidationResult:
        """スキーマ検証"""
        
    def create_backup(self, backup_name: str) -> BackupResult:
        """バックアップ作成"""
        
    def restore_backup(self, backup_name: str) -> RestoreResult:
        """バックアップ復元"""
        
    def apply_partial(self, tables: list[str], options: ApplyOptions):
        """部分適用"""
```

---

## 🗓️ 実装優先度と依存関係

### Phase 1 (高優先度) - 基盤強化
1. **スキーマバージョン管理システム** (2ヶ月)
   - 他の機能の基盤となる
   - 既存機能への影響が大きい

2. **DB適用コマンド拡充** (1ヶ月)
   - 既存機能の拡張
   - リスクが低い

3. **ビュー管理機能の拡張** (2ヶ月)
   - 現在の基本実装から高度な機能への発展
   - SQL解析エンジンは他機能でも活用可能

### Phase 2 (中優先度) - 機能拡張
4. **ドキュメント生成機能** (1.5ヶ月)
   - スキーマ管理システムに依存

5. **MCPサーバー化** (2ヶ月)
   - 独立した機能
   - 新しい価値を提供

### Phase 3 (低優先度) - UI改善
6. **Shadcn/UI移行** (3ヶ月)
   - 大規模なリファクタリング
   - 機能への影響は少ない

## 📋 実装時の考慮事項

### 技術的制約
- 既存API の後方互換性維持
- パフォーマンスの劣化防止
- テストカバレッジの維持

### 運用考慮事項
- 既存プロジェクトのマイグレーション方法
- ドキュメントの更新
- ユーザーへの移行ガイド提供

### リスク管理
- 大規模変更時の段階的デプロイ
- フィーチャーフラグによる機能切り替え
- ロールバック計画の策定

---

## 🔧 dbio拡張対応（緊急・高優先度）

**目的**: 拡張されたschema機能に対応するためのdbio module修正

### 必要な対応（優先度順）

#### 🚨 緊急対応（システム動作に必須）
1. **Field→Column移行対応**
   - `packages/dbgear/dbgear/core/dbio/table.py:4` - `Field`を`Column`にimport修正
   - `table.fields` → `table.columns` の属性名変更
   - 全ての`Field`型参照を`Column`型に変更

2. **ColumnType対応**
   - 現在：文字列の`column_type`を想定
   - 新規：`ColumnType`オブジェクトから`column_type`文字列を抽出する処理追加

#### 🔧 高優先度対応（主要機能拡張）
3. **MySQL表オプション対応**
   - `MySQLTableOptions`の`CREATE TABLE`文への反映
   - エンジン、文字セット、照合順序、パーティション対応

4. **外部キー制約対応**
   - `Relation`モデルから物理FK制約の生成
   - `constraint_name`, `on_delete`, `on_update`オプション対応
   - FK制約の作成・削除機能

5. **高度なインデックス対応**
   - インデックスタイプ（BTREE, HASH, FULLTEXT等）
   - UNIQUE制約
   - 複合インデックスの詳細設定

### SQL テンプレートエンジン化の提案

**目的**: SQLの生成を保守しやすいテンプレート形式で管理

#### アーキテクチャ案

```python
# dbgear/core/dbio/templates/ モジュール
dbgear/
  core/
    dbio/
      templates/
        __init__.py
        engine.py              # テンプレートエンジン基盤
        mysql/
          __init__.py
          table_ddl.py         # CREATE TABLE テンプレート
          index_ddl.py         # CREATE INDEX テンプレート
          constraint_ddl.py    # 制約関連テンプレート
          view_ddl.py          # CREATE VIEW テンプレート
        postgresql/           # 将来の拡張用
          __init__.py
        sqlite/              # 将来の拡張用
          __init__.py
```

#### テンプレートエンジン選択肢

1. **Jinja2**（推奨）
   ```python
   # CREATE TABLE テンプレート例
   CREATE TABLE {{ table.table_name }} (
   {%- for column in table.columns %}
     {{ column.column_name }} {{ column.column_type.column_type }}
     {%- if column.column_type.length %} ({{ column.column_type.length }}){% endif %}
     {%- if not column.nullable %} NOT NULL{% endif %}
     {%- if column.auto_increment %} AUTO_INCREMENT{% endif %}
     {%- if column.default_value %} DEFAULT {{ column.default_value }}{% endif %}
     {%- if column.expression %} AS ({{ column.expression }}) {% if column.stored %}STORED{% else %}VIRTUAL{% endif %}{% endif %}
     {%- if column.charset %} CHARACTER SET {{ column.charset }}{% endif %}
     {%- if column.collation %} COLLATE {{ column.collation }}{% endif %}
     {%- if not loop.last %},{% endif %}
   {%- endfor %}
   {%- if table.get_primary_key_columns() %}
     , PRIMARY KEY ({{ table.get_primary_key_columns() | join(', ') }})
   {%- endif %}
   {%- for relation in table.relations %}
     {%- if relation.constraint_name %}
     , CONSTRAINT {{ relation.constraint_name }} 
       FOREIGN KEY ({{ relation.bind_columns | map(attribute='source_column') | join(', ') }})
       REFERENCES {{ relation.target.table_name }} ({{ relation.bind_columns | map(attribute='target_column') | join(', ') }})
       {%- if relation.on_delete != 'RESTRICT' %} ON DELETE {{ relation.on_delete }}{% endif %}
       {%- if relation.on_update != 'RESTRICT' %} ON UPDATE {{ relation.on_update }}{% endif %}
     {%- endif %}
   {%- endfor %}
   )
   {%- if table.mysql_options %}
   {%- if table.mysql_options.engine %} ENGINE={{ table.mysql_options.engine }}{% endif %}
   {%- if table.mysql_options.charset %} DEFAULT CHARSET={{ table.mysql_options.charset }}{% endif %}
   {%- if table.mysql_options.collation %} COLLATE={{ table.mysql_options.collation }}{% endif %}
   {%- if table.mysql_options.auto_increment %} AUTO_INCREMENT={{ table.mysql_options.auto_increment }}{% endif %}
   {%- endif %}
   ```

2. **Python string.Template**（軽量）
   ```python
   CREATE_TABLE_TEMPLATE = """
   CREATE TABLE $table_name (
       $column_definitions
       $primary_key_constraint
       $foreign_key_constraints
   ) $table_options
   """
   ```

3. **カスタムビルダー**（型安全）
   ```python
   class MySQLTableBuilder:
       def __init__(self, table: Table):
           self.table = table
           
       def build_create_statement(self) -> str:
           parts = [
               f"CREATE TABLE {self.table.table_name} (",
               self._build_column_definitions(),
               self._build_constraints(),
               f") {self._build_table_options()}"
           ]
           return "\n".join(parts)
   ```

#### 実装ステップ（推奨：Jinja2）

```bash
# Phase 1: テンプレートエンジン基盤 (1週間)
- Jinja2の統合
- 基本テンプレート構造の設計
- MySQL用テンプレートファイルの作成

# Phase 2: 既存機能の移行 (1週間)
- table.py の CREATE TABLE 生成をテンプレート化
- index.py の CREATE INDEX 生成をテンプレート化
- view.py の CREATE VIEW 生成をテンプレート化

# Phase 3: 新機能の実装 (2週間)
- 外部キー制約テンプレート
- MySQL表オプションテンプレート
- 高度なインデックステンプレート

# Phase 4: テスト・検証 (1週間)
- 生成されるSQLの検証
- 既存テストの修正
- 新機能のテストケース追加
```

#### 利点
- **保守性**: SQLロジックとPythonロジックの分離
- **可読性**: テンプレートファイルで直観的にSQL構造を把握
- **拡張性**: 新しいDB種別やオプションの追加が容易
- **テスト性**: テンプレートとデータを分離してテスト可能
- **一貫性**: 全てのSQL生成が統一されたパターンに従う

---

*このロードマップは開発の進捗に応じて随時更新されます。*