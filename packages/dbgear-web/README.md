# DBGear Web

DBGearのWebインターフェースです。直感的なUIでデータベースの初期データを編集できます。

## インストール

```bash
pip install dbgear-web
```

`dbgear`パッケージが自動的に依存関係としてインストールされます。

## 使用方法

### Webサーバーの起動

```bash
# 基本的な使用方法
dbgear-web --project ./my-project

# オプション指定
dbgear-web --project ./my-project --port 8080 --host 0.0.0.0
```

ブラウザで http://localhost:5000 （または指定したポート）にアクセスしてください。

### コマンドラインオプション

- `--project PROJECT_DIR`: プロジェクトディレクトリ (デフォルト: database)
- `--port PORT`: ポート番号 (デフォルト: 5000)
- `--host HOST`: ホスト名 (デフォルト: 0.0.0.0)

## 機能

### Web UI機能
- **データグリッド編集**: テーブル形式でのデータ編集
- **マトリックス編集**: 権限設定などのマトリックス形式データ編集
- **単一レコード編集**: 設定値などの単一レコード編集
- **関連データ参照**: 外部キー参照の自動解決
- **リアルタイム更新**: 編集内容の即座な反映

### スキーマ管理機能（新機能）
- **スキーマ管理**: データベーススキーマの作成・削除・更新
- **テーブル管理**: テーブル定義のCRUD操作
- **カラム管理**: カラム定義の作成・編集・削除
- **インデックス管理**: インデックスの作成・削除（自動命名対応）
- **ビュー管理**: データベースビューの定義・編集
- **スキーマ検証**: テーブル・カラム・外部キー制約の検証

### 対応データレイアウト
- **Table**: 通常のテーブル形式
- **Matrix**: マトリックス形式（権限設定等）
- **Single**: 単一レコード形式（システム設定等）

## 前提条件

DBGear Webを使用するには、事前にプロジェクト設定が必要です：

1. `project.yaml`の作成
2. スキーマ定義の配置（A5:SQL Mk-2ファイル等）
3. 環境設定の作成（`_mapping.yaml`）

詳細は[dbgearパッケージのドキュメント](https://pypi.org/project/dbgear/)を参照してください。

## 技術仕様

- **バックエンド**: FastAPI
- **フロントエンド**: React + TypeScript + Material-UI
- **通信**: REST API
- **データ形式**: YAML

### API エンドポイント

#### スキーマ管理API
- `GET /api/schemas` - スキーマ一覧取得
- `POST /api/schemas` - スキーマ作成
- `GET /api/schemas/{schema_name}` - スキーマ詳細取得
- `DELETE /api/schemas/{schema_name}` - スキーマ削除

#### テーブル管理API
- `GET /api/schemas/{schema_name}/tables` - テーブル一覧取得
- `POST /api/schemas/{schema_name}/tables` - テーブル作成
- `GET /api/schemas/{schema_name}/tables/{table_name}` - テーブル詳細取得
- `PUT /api/schemas/{schema_name}/tables/{table_name}` - テーブル更新
- `DELETE /api/schemas/{schema_name}/tables/{table_name}` - テーブル削除

#### カラム管理API
- `GET /api/schemas/{schema_name}/tables/{table_name}/columns` - カラム一覧取得
- `POST /api/schemas/{schema_name}/tables/{table_name}/columns` - カラム作成
- `GET /api/schemas/{schema_name}/tables/{table_name}/columns/{column_name}` - カラム詳細取得
- `PUT /api/schemas/{schema_name}/tables/{table_name}/columns/{column_name}` - カラム更新
- `DELETE /api/schemas/{schema_name}/tables/{table_name}/columns/{column_name}` - カラム削除

#### インデックス管理API
- `GET /api/schemas/{schema_name}/tables/{table_name}/indexes` - インデックス一覧取得
- `POST /api/schemas/{schema_name}/tables/{table_name}/indexes` - インデックス作成
- `DELETE /api/schemas/{schema_name}/tables/{table_name}/indexes/{index_name}` - インデックス削除

#### ビュー管理API
- `GET /api/schemas/{schema_name}/views` - ビュー一覧取得
- `POST /api/schemas/{schema_name}/views` - ビュー作成
- `GET /api/schemas/{schema_name}/views/{view_name}` - ビュー詳細取得
- `PUT /api/schemas/{schema_name}/views/{view_name}` - ビュー更新
- `DELETE /api/schemas/{schema_name}/views/{view_name}` - ビュー削除

#### スキーマ検証API
- `POST /api/schemas/validate/table` - テーブル検証
- `POST /api/schemas/validate/column` - カラム検証
- `POST /api/schemas/validate/foreign-key` - 外部キー検証
- `GET /api/schemas/{schema_name}/validate` - スキーマ全体検証

## 開発

### ローカル開発
```bash
# リポジトリをクローン
git clone https://github.com/tamuto/dbgear.git
cd dbgear/packages/dbgear-web

# 依存関係をインストール
poetry install
```

### 開発タスク
```bash
task test           # 全テスト実行
task test-fast      # 軽量テストのみ
task lint           # flake8によるコードチェック
task clean          # ビルド成果物のクリーンアップ
task serve          # 開発サーバー起動（テストプロジェクト使用）
```

### フロントエンド開発
```bash
# プロジェクトルートで
npm run watch  # ウォッチモード
npm run build  # ビルド
```

## ライセンス

MIT