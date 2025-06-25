# DataModel.yaml 仕様書

## 概要

`DataModel.yaml`は、DBGearプロジェクトのデータモデル設定を定義するファイルです。Webインターフェースのデータグリッドレイアウト、フィールド設定、同期モードを管理し、テーブル、マトリックス、単一値の3つのレイアウトに対応します。

## ファイル配置

`DataModel.yaml`は各環境ディレクトリ内のマッピングサブディレクトリに配置します。ファイル名は`{schema_name}@{table_name}.yaml`の形式で命名されます。

```
project-root/
├── project.yaml          # プロジェクト設定ファイル
├── schema.yaml           # スキーマ定義ファイル
├── development/          # 開発環境ディレクトリ
│   ├── environ.yaml      # 環境設定ファイル
│   └── base/             # ベースマッピングディレクトリ
│       ├── _mapping.yaml # マッピング設定ファイル
│       ├── main@users.yaml     # ユーザーテーブルのデータモデル
│       ├── main@products.yaml  # 商品テーブルのデータモデル
│       ├── main@orders.yaml    # 注文テーブルのデータモデル
│       ├── main@users.dat      # ユーザーテーブルのデータファイル
│       └── main@products.dat   # 商品テーブルのデータファイル
└── production/           # 本番環境ディレクトリ
```

## 基本構造

### 必須項目

```yaml
schema_name: schema_name
table_name: table_name
description: Description
layout: table
settings: {}
sync_mode: drop_create
```

### 項目詳細

#### schema_name
- **型**: 文字列
- **必須**: はい
- **説明**: 対象スキーマ名
- **例**: `main`, `user_db`, `log_db`

#### table_name
- **型**: 文字列
- **必須**: はい
- **説明**: 対象テーブル名
- **例**: `users`, `products`, `orders`

#### description
- **型**: 文字列
- **必須**: はい
- **説明**: データモデルの概要説明。日本語使用可能
- **例**: `ユーザーマスター`, `商品情報管理`, `注文データ`

#### layout
- **型**: 文字列
- **必須**: はい
- **説明**: データグリッドのレイアウト種別
- **値**: 
  - `table`: 通常のテーブル形式
  - `matrix`: マトリックス形式（権限設定など）
  - `single`: 単一レコード形式（設定値など）

#### settings
- **型**: オブジェクト
- **必須**: はい
- **説明**: フィールド別の設定情報
- **子要素**:
  - `type`: 設定種別（`refs`, `now`, `update_user`, `echo`など）
  - `width`: 表示幅（オプション）
  - `environ`: 環境名（オプション）
  - `schema_name`: 参照スキーマ名（オプション）
  - `table_name`: 参照テーブル名（オプション）

#### sync_mode
- **型**: 文字列
- **必須**: はい
- **説明**: データ同期モード
- **値**:
  - `drop_create`: テーブルを削除して再作成
  - `delta`: 差分のみ同期
  - `append`: 追加のみ

#### matrix レイアウト専用項目
- `x_axis`: X軸のカラム名
- `y_axis`: Y軸のカラム名
- `cells`: セル値のカラム名リスト

#### single レイアウト専用項目
- `value`: 値カラム名
- `caption`: キャプション

#### セグメント対応
- `segment`: セグメント名（データファイルの分割管理）

## 設定例

### Table レイアウト

```yaml
schema_name: main
table_name: users
description: ユーザーマスター
layout: table
settings:
  id:
    type: auto_increment
  name:
    type: echo
  email:
    type: echo
sync_mode: drop_create
```

### Matrix レイアウト

```yaml
schema_name: main
table_name: permissions
description: 権限マトリックス
layout: matrix
settings:
  user_id:
    type: refs
    schema_name: main
    table_name: users
  role_id:
    type: refs
    schema_name: main
    table_name: roles
sync_mode: drop_create
x_axis: user_id
y_axis: role_id
cells:
  - permission_level
```

## データファイル管理

データモデルに対応するデータファイル（`.dat`）が同じディレクトリに配置されます：

- **単一ファイル**: `{schema_name}@{table_name}.dat`
- **セグメント分割**: `{schema_name}@{table_name}#{segment}.dat`

この仕様により、DBGearプロジェクトのデータモデル設定を統一的に管理できます。