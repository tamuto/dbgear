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

# Phase 3: Web UI対応
- スキーマエディター機能
- マイグレーション管理画面
- バージョン履歴表示

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

### 5. DB適用コマンドの拡充

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

### Phase 2 (中優先度) - 機能拡張
3. **ドキュメント生成機能** (1.5ヶ月)
   - スキーマ管理システムに依存

4. **MCPサーバー化** (2ヶ月)
   - 独立した機能
   - 新しい価値を提供

### Phase 3 (低優先度) - UI改善
5. **Shadcn/UI移行** (3ヶ月)
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

*このロードマップは開発の進捗に応じて随時更新されます。*