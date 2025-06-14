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

## 開発

### ローカル開発
```bash
# リポジトリをクローン
git clone https://github.com/tamuto/dbgear.git
cd dbgear/packages/dbgear-web

# 依存関係をインストール
poetry install

# 開発サーバー起動
poetry run python -m dbgear_web.main --project ../../etc/test
```

### フロントエンド開発
```bash
# プロジェクトルートで
npm run watch  # ウォッチモード
npm run build  # ビルド
```

## ライセンス

MIT