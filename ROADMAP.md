# DBGear 機能拡張ロードマップ

DBGearの将来的な機能拡張計画と実装指針をまとめたドキュメントです。

## 🎯 計画中の機能拡張

### 1. ER図レイアウトライブラリの統合

**目的**: Cytoscape.jsに代わる新しいレイアウトライブラリの統合

**現在の状況**: ER図表示機能は実装済みだが、レイアウトライブラリが未確定

**実装ステップ**:
```bash
# Phase 1: ライブラリ選定
- D3.js vs Vis.js vs その他の評価
- パフォーマンステスト
- FastHTML統合性の確認

# Phase 2: 統合実装
- 選択したライブラリの統合
- 既存ER図機能との連携
- レスポンシブ対応

# Phase 3: 高度な機能
- インタラクティブなノード操作
- レイアウトアルゴリズムの選択機能
- エクスポート機能（SVG, PNG）
```

**優先度**: 高（現在進行中）

---

### 2. 柔軟なスキーマファイル管理システム

**目的**: schema.yamlのファイル名指定による環境別・バージョン別スキーマ管理

**現在の課題**:
- 環境ごとに異なるスキーマバージョンを管理したい
- 開発・テスト・本番で異なるスキーマファイルを使い分けたい
- マイグレーション履歴をファイルレベルで管理したい

**新機能設計**:
```yaml
# project.yaml (環境別スキーマファイル指定)
project_name: MyProject
description: Database initial data management

schema_files:
  development: schema_v2.1_dev.yaml
  testing: schema_v2.0_stable.yaml
  production: schema_v1.9_prod.yaml
  feature_branch: schema_v2.2_experimental.yaml

environments:
  development:
    schema_file: schema_v2.1_dev.yaml
    deploy_target: localhost_dev
  testing:
    schema_file: schema_v2.0_stable.yaml
    deploy_target: localhost_test
  production:
    schema_file: schema_v1.9_prod.yaml
    deploy_target: prod_server
```

**実装ステップ**:
```bash
# Phase 1: スキーマファイル管理基盤
- Project.pyにschema_files設定の追加
- 環境別スキーマファイル読み込み機能
- SchemaManagerの動的ファイル指定対応

# Phase 2: CLI統合
- dbgear apply --schema-file オプション追加
- 環境別適用コマンドの拡張
- スキーマファイル切り替え機能

# Phase 3: Web UI統合
- スキーマファイル選択機能
- 環境別スキーマ表示
- ファイル間差分表示機能

# Phase 4: 履歴管理機能
- スキーマファイル履歴追跡
- 変更履歴可視化
- ロールバック機能
```

**新CLIコマンド**:
```bash
dbgear apply localhost development --schema-file schema_v2.1.yaml
dbgear schema diff schema_v1.9.yaml schema_v2.0.yaml
dbgear schema list                           # 利用可能スキーマファイル一覧
dbgear schema switch development v2.1        # 環境のスキーマファイル切り替え
```

**優先度**: 高

---

### 3. データベーススキーマチェック機能

**目的**: schema.yamlと実際のデータベースの乖離検出・分析機能

**機能詳細**:
- 実DBスキーマとYAML定義の差分検出
- カラム型、制約、インデックスの不一致確認
- 実DBに存在するがYAMLに未定義のオブジェクト検出
- YAMLに定義されているが実DBに存在しないオブジェクト検出

**実装アーキテクチャ**:
```python
# dbgear/validation/ モジュール
dbgear/
  validation/
    __init__.py
    schema_checker.py      # メインチェッカークラス
    db_inspector.py        # データベース構造検査
    diff_analyzer.py       # 差分分析
    report_generator.py    # レポート生成
```

**機能設計**:
```python
class SchemaChecker:
    def check_schema_consistency(self, schema_file: str, environment: str) -> ValidationReport:
        """スキーマ整合性チェック"""
        
    def detect_schema_drift(self, schema_file: str, environment: str) -> DriftReport:
        """スキーマドリフト検出"""
        
    def suggest_schema_fixes(self, validation_report: ValidationReport) -> list[SchemeFix]:
        """修正提案生成"""
        
    def generate_migration_sql(self, diff_result: DiffResult) -> str:
        """差分を解決するSQL生成"""
```

**チェック項目**:
```yaml
# 検出する差分タイプ
table_differences:
  - missing_tables          # YAML定義済みだがDB未作成
  - extra_tables            # DB存在だがYAML未定義
  - table_option_mismatch   # エンジン、文字セット等の不一致

column_differences:
  - missing_columns         # 不足カラム
  - extra_columns          # 余分なカラム  
  - type_mismatch          # 型不一致
  - nullable_mismatch      # NULL制約不一致
  - default_value_mismatch # デフォルト値不一致

constraint_differences:
  - missing_primary_keys   # 主キー不一致
  - missing_foreign_keys   # 外部キー不一致
  - missing_unique_keys    # ユニーク制約不一致
  - extra_constraints      # 余分な制約

index_differences:
  - missing_indexes        # 不足インデックス
  - extra_indexes         # 余分なインデックス
  - index_definition_mismatch # インデックス定義不一致
```

**実装ステップ**:
```bash
# Phase 1: 基本チェック機能
- データベース構造検査機能
- 基本的な差分検出（テーブル、カラム）
- シンプルなレポート生成

# Phase 2: 高度なチェック機能
- 制約・インデックス差分検出
- 詳細な差分分析
- 修正提案機能

# Phase 3: CLI統合
- dbgear check コマンドの追加
- 差分表示・レポート機能
- 自動修正SQL生成

# Phase 4: Web UI統合
- スキーマチェック画面
- 差分可視化機能
- ワンクリック修正機能
```

**CLIコマンド**:
```bash
dbgear check localhost development                    # 基本チェック
dbgear check localhost development --detailed         # 詳細チェック
dbgear check localhost development --fix-sql         # 修正SQL生成
dbgear check localhost development --auto-fix        # 自動修正実行
dbgear check --all-environments                      # 全環境チェック
```

**優先度**: 中

---

### 4. ビュー管理機能の拡張

**目的**: 現在のシンプルなビュー定義から高度なSQL解析・依存関係管理への発展

**現在の実装状況**:
- ✅ 基本的なビュー定義 (YAML形式でSQL文のみ記述)
- ✅ データベースビューのCRUD操作
- ✅ 基本的な依存関係チェック機能

**将来の拡張機能**:

#### Phase 1: SQL解析エンジンの導入
```python
# dbgear/analysis/ モジュール
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

#### Phase 2: 高度な依存関係管理
```python
class ViewDependencyManager:
    def analyze_impact(self, table_name: str) -> ImpactAnalysis:
        """テーブル変更時の影響範囲を分析"""
        
    def suggest_view_updates(self, schema_changes: list[SchemaChange]) -> list[ViewUpdate]:
        """スキーマ変更に応じたビュー更新を提案"""
        
    def generate_view_creation_order(self, views: dict[str, View]) -> list[str]:
        """依存関係を考慮したビュー作成順序を生成"""
```

#### Phase 3: CLI機能拡張
```bash
dbgear view list                           # ビュー一覧表示
dbgear view analyze user_summary           # 指定ビューの分析
dbgear view dependencies user_summary      # 依存関係表示
dbgear view impact users                   # テーブル変更の影響分析
dbgear view validate                       # 全ビューの整合性チェック
```

**技術的依存関係**:
- sqlparse or pglast (SQL解析)
- networkx (依存関係グラフ)

**優先度**: 中

---

### 5. A5:SQL Mk-2 インポート機能の完成

**目的**: 現在コア機能として実装されているA5:SQL Mk-2インポート機能のCLI統合

**現在の状況**: 
- ✅ コア機能: `misc/a5sql_mk2.py`で実装済み
- 🔄 CLI統合: `dbgear import`コマンド未実装

**実装ステップ**:
```bash
# Phase 1: CLI統合
- main.pyにimportサブコマンド追加
- A5:SQL Mk-2インポート機能のCLI統合
- エラーハンドリング強化

# Phase 2: 機能拡張
- スキーママッピング機能
- カスタム出力フォーマット対応
- バリデーション強化

# Phase 3: Web UI統合
- インポート機能のWeb UI化
- ファイルアップロード機能
- プレビュー機能
```

**CLIコマンド**:
```bash
dbgear import a5sql_mk2 schema.a5er                    # 基本インポート
dbgear import a5sql_mk2 schema.a5er --output out.yaml  # 出力ファイル指定
dbgear import a5sql_mk2 schema.a5er --mapping "MAIN:main,TEST:test"  # スキーママッピング
```

**優先度**: 低

---

### 6. ドキュメント生成機能

**目的**: スキーマ定義からER図とテーブル定義書の自動生成

**現在の状況**: Web Editorでオンデマンド照会が可能

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
      er_diagram.py      # 統合されたライブラリを使用
      table_spec.py      # HTMLテンプレート生成
      base.py           # 共通基底クラス
    templates/
      table_spec.html    # Jinja2テンプレート
      schema_overview.html
    exporters/
      __init__.py
      pdf.py            # WeasyPrintを使用
      svg.py
```

**実装ステップ**:
```bash
# Phase 1: テーブル定義書生成
- HTMLテンプレートによる定義書生成
- 既存のSchemaManager統合
- PDF出力機能

# Phase 2: ER図生成
- 統合されたレイアウトライブラリを使用
- SVG/PNG出力機能
- カスタマイズ機能

# Phase 3: CLI統合
- dbgear docs コマンドの追加
- 出力形式の選択機能
- テンプレートカスタマイズ

# Phase 4: Web UI統合強化
- ドキュメント生成画面
- リアルタイムプレビュー
- ダウンロード機能
```

**CLIコマンド**:
```bash
dbgear docs er --output diagram.svg         # ER図生成
dbgear docs tables --format pdf             # テーブル定義書生成
dbgear docs all --output-dir ./docs         # 全ドキュメント生成
```

**依存関係**:
- 統合予定のレイアウトライブラリ (ER図生成)
- Jinja2 (テンプレートエンジン) - 既に使用中
- WeasyPrint (PDF生成)

**優先度**: 低

---

### 7. DB適用コマンドの拡充

**目的**: より安全で柔軟なデータベース操作機能

**新機能**:
- データバックアップ機能強化
- ドライラン機能
- 部分適用機能

**拡張コマンド**:
```bash
# ドライラン機能
dbgear apply --dry-run localhost test        # 実際には実行しない

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
```

**実装ステップ**:
```bash
# Phase 1: バックアップ機能
- 自動バックアップ機能
- 世代管理機能
- 復元機能

# Phase 2: 高度な適用機能
- 部分適用機能
- ドライラン機能
- トランザクション管理強化

# Phase 3: セーフティ機能
- 適用前確認機能
- 自動ロールバック機能
- 詳細ログ機能
```

**優先度**: 低

---

## 🗓️ 実装優先度とスケジュール

### Phase 1 (高優先度) - 現在進行中/次期実装
1. **ER図レイアウトライブラリ統合** (1ヶ月) - 🔄 現在進行中
2. **柔軟なスキーマファイル管理システム** (2ヶ月)

### Phase 2 (中優先度) - 主要機能拡張
3. **データベーススキーマチェック機能** (1.5ヶ月)
4. **ビュー管理機能の拡張** (2ヶ月)

### Phase 3 (低優先度) - 利便性向上
5. **A5:SQL Mk-2インポートCLI統合** (2週間)
6. **ドキュメント生成機能** (1.5ヶ月)
7. **DB適用コマンド拡充** (1ヶ月)

## 📋 実装時の考慮事項

### 技術的制約
- 既存APIの後方互換性維持
- FastHTML アーキテクチャとの整合性
- Pydanticモデルとの統合
- 既存のSQLテンプレートエンジンとの連携

### 運用考慮事項
- 既存プロジェクトへの影響を最小化
- 段階的な機能追加による安定性確保
- ユーザビリティの継続的改善

### リスク管理
- 大規模変更時の段階的デプロイ
- フィーチャーフラグによる機能切り替え
- ロールバック計画の策定

---

## 🏗️ アーキテクチャの方針

### 既存基盤との統合原則
1. **既存パターンの踏襲**: Managerパターン、Pydanticモデルを継続使用
2. **テンプレートエンジン活用**: 新しいSQL生成はテンプレートベースで実装
3. **FastHTML統合**: Web UI機能は3-pane layoutパターンを継続
4. **段階的実装**: 大きな変更は段階的にリリース

### 新機能開発指針
- 既存の依存関係管理システムとの統合
- CLI/Web UI両方での機能提供
- テスタビリティを重視した設計
- パフォーマンスへの影響を最小化

---

*このロードマップは開発の進捗に応じて随時更新されます。*