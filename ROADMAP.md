# DBGear 機能拡張ロードマップ

DBGearの将来的な機能拡張計画と実装指針をまとめたドキュメントです。

## ✅ 完了した主要機能 (2024-2025)

### Web エディター (FastHTML)
- **3-Pane Layout System**: メインコンテンツ、サイドバー、右サイドバーの効率的レイアウト
- **統合Notes表示**: 全エンティティ（テーブル、ビュー、プロシージャ、トリガー）対応のドキュメント管理
- **Dependencies可視化**: テーブル依存関係の双方向表示機能
- **包括的スキーマ管理**: テーブル、ビュー、プロシージャ、トリガーのCRUD操作

### コアアーキテクチャ
- **Managerパターン**: SchemaManager、TableManager、ViewManager等の統一CRUDインターフェース
- **Pydanticモデル**: 完全な型安全性と自動検証を備えたモデルシステム
- **SQLテンプレートエンジン**: 21個のMySQLテンプレートによる統一されたSQL生成システム
- **JSONデータサポート**: MySQL JSON型とYAMLデータファイルのシームレスな連携

### 依存関係管理システム
- **TableDependencyAnalyzer**: テーブル依存関係の階層的分析機能
- **DependencyResolver**: データ挿入順序の自動最適化と循環依存検出
- **テンプレートベースSQL**: `dbgear/dbio/templates/` による保守性の高いSQL生成

### MCPサーバー統合
- **dbgear-mcpパッケージ**: LLM統合のためのMCPサーバー実装
- **FastMCP**: 高速なMCPサーバー基盤

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

### 2. 内蔵スキーマバージョン管理システム

**目的**: 外部ツールに依存しない独自のスキーマ管理とマイグレーション機能

**新機能設計**:
```yaml
# schema.yaml (拡張フォーマット)
version: "1.2.0"
schemas:
  main:
    tables:
      users:
        version: "1.1.0"
        columns:
          - column_name: id
            column_type:
              column_type: BIGINT
              base_type: BIGINT
            primary_key: 1
            auto_increment: true
          - column_name: name
            column_type:
              column_type: VARCHAR
              length: 255
            nullable: false
            
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
# Phase 1: バージョン管理基盤
- スキーマバージョニングシステム
- マイグレーション定義フォーマット
- 差分検出機能

# Phase 2: マイグレーション実行エンジン
- マイグレーション実行機能
- ロールバック機能
- トランザクション管理

# Phase 3: CLI統合
- dbgear migrate コマンド群
- バージョン管理コマンド
- 差分表示機能

# Phase 4: Web UI統合
- マイグレーション管理画面
- バージョン履歴表示
- 差分可視化
```

**新CLIコマンド**:
```bash
dbgear schema init                    # 新規スキーマ作成
dbgear schema diff                    # スキーマ差分表示
dbgear migrate up                     # マイグレーション実行
dbgear migrate down                   # ロールバック実行
dbgear migrate status                 # マイグレーション状況確認
```

**優先度**: 高

---

### 3. A5:SQL Mk-2 インポート機能の完成

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

**優先度**: 中

---

### 4. ドキュメント生成機能

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
      er_diagram.py      # 選定されたライブラリを使用
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

# Phase 4: Web UI統合
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

**優先度**: 中

---

### 5. ビュー管理機能の拡張

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
- ドライラン機能
- トランザクション管理強化
```

**優先度**: 低

---

## 🗓️ 実装優先度とスケジュール

### Phase 1 (高優先度) - 現在進行中/次期実装
1. **ER図レイアウトライブラリ統合** (1ヶ月) - 🔄 現在進行中
2. **A5:SQL Mk-2インポートCLI統合** (2週間)
3. **スキーマバージョン管理システム** (2ヶ月)

### Phase 2 (中優先度) - 機能拡張
4. **ドキュメント生成機能** (1.5ヶ月)
   - スキーマ管理システムに依存
5. **ビュー管理機能の拡張** (2ヶ月)
   - SQL解析エンジンは他機能でも活用可能

### Phase 3 (低優先度) - 利便性向上
6. **DB適用コマンド拡充** (1ヶ月)
   - 既存機能の拡張

## 📋 実装時の考慮事項

### 技術的制約
- 既存APIの後方互換性維持
- FastHTML アーキテクチャとの整合性
- Pydanticモデルとの統合
- 既存のSQLテンプレートエンジンとの連携

### 運用考慮事項
- 既存プロジェクトのマイグレーション方法
- ドキュメントの更新
- ユーザーへの移行ガイド提供

### リスク管理
- 大規模変更時の段階的デプロイ
- フィーチャーフラグによる機能切り替え
- ロールバック計画の策定

---

## 🏗️ アーキテクチャの方針

### 現在の強固な基盤を活用
- ✅ Pydanticベースのモデルシステム
- ✅ Managerパターンによる統一CRUD
- ✅ SQLテンプレートエンジン
- ✅ FastHTML Webアーキテクチャ
- ✅ 依存関係管理システム

### 新機能統合の原則
1. **既存パターンの踏襲**: Managerパターン、Pydanticモデルを継続使用
2. **テンプレートエンジン活用**: 新しいSQL生成はテンプレートベースで実装
3. **FastHTML統合**: Web UI機能は3-pane layoutパターンを継続
4. **段階的実装**: 大きな変更は段階的にリリース

---

*このロードマップは開発の進捗に応じて随時更新されます。*