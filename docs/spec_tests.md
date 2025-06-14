# DBGear ユニットテスト仕様書

このドキュメントでは、DBGearプロジェクトのユニットテストの内容、管理方針、品質指標について説明します。

## 📋 作成したユニットテストの概要

### 1. **MySQL定義パーサーテスト** (`test_mysql.py`)

```python
# 実際のテスト例
def test_build_fields_basic(self):
    # モックデータでデータベースの列情報をシミュレート
    mock_columns = [
        MockRow(COLUMN_NAME='id', COLUMN_TYPE='int(11)', 
                IS_NULLABLE='NO', COLUMN_KEY='PRI'),
        MockRow(COLUMN_NAME='name', COLUMN_TYPE='varchar(100)', 
                IS_NULLABLE='YES')
    ]
    
    # 実際の関数をテスト
    fields = build_fields(connection, 'test_db', 'users', {'id': 1})
    
    # 結果を検証
    self.assertEqual(len(fields), 2)
    self.assertEqual(fields[0].column_name, 'id')
    self.assertTrue(fields[0].primary_key)
```

**何をテストしているか:**
- データベース接続なしでパーサーロジックをテスト
- プライマリキー、インデックス、複合キーの処理
- エラーハンドリング（接続失敗など）
- 複数スキーマのマッピング

### 2. **MySQL統合テスト** (`test_mysql_integration.py`)

```python
def test_mysql_connection_and_schema_retrieval(self):
    try:
        # 実際のMySQLサーバーに接続
        schemas = retrieve(
            connect='mysql+pymysql://root:password@host.docker.internal',
            mapping={'test': 'main'}
        )
        print(f"成功: {len(schemas)}個のスキーマを取得")
    except Exception as e:
        # 接続できない場合はテストをスキップ
        self.skipTest(f"MySQL connection failed: {e}")
```

**何をテストしているか:**
- 実際のデータベースへの接続確認
- 本物のスキーマ情報の取得
- information_schemaへのアクセス
- 接続エラーの適切な処理

### 3. **A5:ER定義パーサーテスト** (`test_a5sql_mk2.py`)

```python
def test_parser_basic_entity_parsing(self):
    parser = Parser(mapping)
    
    # A5:ERファイル形式の解析をテスト
    parser.parse_line(1, '[Entity]')
    parser.parse_line(2, 'PName=users')
    parser.parse_line(3, 'Field="ID","id","int","NOT NULL",0,"",""')
    
    # 解析結果を検証
    entity = parser.instances['main'][0]
    self.assertEqual(entity.table_name, 'users')
```

**何をテストしているか:**
- A5:ERファイル形式の正確な解析
- エンティティ、リレーション、インデックスの処理
- 日本語文字の処理（UTF-8、BOM対応）
- CSVフィールド解析のエッジケース

### 4. **選択可能定義パーサーテスト** (`test_selectable.py`)

```python
def test_table_structure(self):
    schemas = retrieve(prefix='_select', items={'test': 'Test'})
    table = schemas['_select'].tables['test']
    
    # 生成されるテーブル構造を検証
    self.assertEqual(len(table.fields), 2)
    self.assertEqual(table.fields[0].column_name, 'value')
    self.assertEqual(table.fields[0].primary_key, 1)
```

**何をテストしているか:**
- ドロップダウン用テーブルの自動生成
- フィールド構造の一貫性
- 特殊文字、Unicode文字の処理
- プレフィックスのバリエーション

## 🔍 ユニットテストが検証している品質

### **1. 機能の正確性**
```python
# 期待する動作が正しく実装されているか
self.assertEqual(field.column_type, 'varchar(100)')
self.assertTrue(field.nullable)
```

### **2. エラーハンドリング**
```python
# 異常系の処理が適切か
with self.assertRaises(Exception):
    retrieve('invalid://connection')
```

### **3. エッジケース**
```python
# 特殊な入力に対する堅牢性
test_items = {
    'test-with-dash': 'Test With Dash',
    'japanese_name': '日本語テスト'
}
```

### **4. インターフェース契約**
```python
# 関数の戻り値の型や構造が仕様通りか
self.assertIsInstance(schemas, dict)
self.assertEqual(len(table.fields), 2)
```

## 📈 ユニットテストの管理方針

### **1. テスト実行の自動化**

```bash
# 開発時の定期実行
task test              # 全テスト実行
task test-fast         # 高速テストのみ

# CI/CDでの自動実行
python -m unittest discover tests/ -v
```

### **2. テストカテゴリ別の管理**

```
tests/
├── definitions/       # 定義パーサーのテスト
│   ├── test_mysql.py             # 単体テスト（高速）
│   └── test_mysql_integration.py # 統合テスト（低速）
├── models/           # データモデルのテスト
└── integration/      # エンドツーエンドテスト
```

### **3. テスト環境の分離**

```python
class TestMySQLIntegration(unittest.TestCase):
    def setUp(self):
        # テスト用のデータベース接続設定
        self.connection_string = 'mysql://test_server'
        
    def tearDown(self):
        # テストデータのクリーンアップ
        cleanup_test_data()
```

### **4. テストデータの管理**

```python
# モックデータの共通化
class MockRow:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# テストフィクスチャの再利用
def setUp(self):
    self.sample_a5er_content = '''
    [Entity]
    PName=test_table
    '''
```

## 🚀 継続的な品質改善

### **1. テスト駆動開発（TDD）**
```python
# 1. 失敗するテストを書く
def test_new_feature(self):
    result = new_function(input_data)
    self.assertEqual(result.status, 'success')

# 2. 最小限の実装で通す
def new_function(data):
    return MockResult(status='success')

# 3. リファクタリングして改善
def new_function(data):
    # 実際のロジックを実装
    return process_data(data)
```

### **2. カバレッジの監視**
```bash
# テストカバレッジの測定
coverage run -m unittest discover
coverage report
coverage html  # HTMLレポート生成
```

### **3. パフォーマンステスト**
```python
def test_large_file_parsing(self):
    start_time = time.time()
    schemas = parse_large_a5er_file()
    duration = time.time() - start_time
    
    self.assertLess(duration, 5.0)  # 5秒以内で処理
    self.assertGreater(len(schemas), 100)  # 100以上のテーブル
```

### **4. 回帰テストの蓄積**
```python
def test_issue_42_fix(self):
    """Issue #42: MySQL接続でUnicodeエラーが発生する問題の修正"""
    connection_string = 'mysql://server?charset=utf8mb4'
    schemas = retrieve(connect=connection_string)
    # 特定のバグが再発しないことを確認
```

## 📊 テスト品質の指標

### **1. カバレッジ目標**
- **単体テスト**: 90%以上のライン/ブランチカバレッジ
- **統合テスト**: 主要なユースケースの80%以上

### **2. テスト分類の比率**
```
単体テスト (70%): 高速、独立性、モック使用
統合テスト (20%): 実際のDB、ファイルI/O
E2Eテスト (10%): 全体の動作確認
```

### **3. 実行時間の管理**
```
高速テスト (<1秒): 開発中に頻繁実行
標準テスト (<30秒): コミット前実行  
完全テスト (<5分): CI/CDで実行
```

## 🔧 メンテナンスのベストプラクティス

### **1. テストの可読性**
```python
def test_mysql_field_parsing_with_unicode_content(self):
    """MySQL定義でUnicode文字を含むフィールド名が正しく処理されることを確認"""
    # Given: Unicode文字を含むフィールド定義
    mock_column = MockRow(COLUMN_NAME='名前', COLUMN_COMMENT='ユーザー名')
    
    # When: フィールドを解析
    field = parse_mysql_field(mock_column)
    
    # Then: Unicode文字が保持される
    self.assertEqual(field.column_name, '名前')
    self.assertEqual(field.comment, 'ユーザー名')
```

### **2. テストの独立性**
```python
def setUp(self):
    """各テスト前にクリーンな状態を確保"""
    self.cleanup_test_files()
    self.reset_database_state()

def tearDown(self):
    """各テスト後にリソースをクリーンアップ"""
    self.cleanup_test_files()
```

### **3. テストの保守性**
```python
# 設定の共通化
TEST_CONFIG = {
    'mysql_connection': 'mysql://test_server',
    'timeout': 30,
    'charset': 'utf8mb4'
}

# ヘルパー関数の活用
def assert_field_properties(self, field, expected_name, expected_type):
    """フィールドプロパティの共通検証"""
    self.assertEqual(field.column_name, expected_name)
    self.assertEqual(field.column_type, expected_type)
```

## 📋 テストケース一覧

### MySQL定義パーサー (`tests/definitions/test_mysql.py`)
| テスト名 | 内容 | カテゴリ |
|---------|------|----------|
| `test_build_fields_basic` | 基本的なフィールド構築 | 単体 |
| `test_build_statistics_primary_and_indexes` | プライマリキーとインデックス | 単体 |
| `test_retrieve_full_schema` | 完全なスキーマ取得 | 単体 |
| `test_build_statistics_composite_primary_key` | 複合プライマリキー | 単体 |
| `test_retrieve_connection_error` | 接続エラーハンドリング | 単体 |
| `test_retrieve_multiple_schemas` | 複数スキーマ対応 | 単体 |
| `test_build_fields_empty_result` | 空の結果処理 | 単体 |
| `test_build_statistics_no_indexes` | インデックスなしのテーブル | 単体 |
| `test_build_statistics_primary_key_only` | プライマリキーのみ | 単体 |

### MySQL統合テスト (`tests/definitions/test_mysql_integration.py`)
| テスト名 | 内容 | カテゴリ |
|---------|------|----------|
| `test_mysql_connection_and_schema_retrieval` | 実際のMySQL接続 | 統合 |
| `test_mysql_empty_database` | 空データベース処理 | 統合 |
| `test_mysql_information_schema_access` | information_schemaアクセス | 統合 |

### A5:ER定義パーサー (`tests/definitions/test_a5sql_mk2.py`)
| テスト名 | 内容 | カテゴリ |
|---------|------|----------|
| `test_parser_basic_entity_parsing` | 基本エンティティ解析 | 単体 |
| `test_parser_relation_parsing` | リレーション解析 | 単体 |
| `test_parser_index_parsing` | インデックス解析 | 単体 |
| `test_convert_to_schema` | スキーマ変換 | 単体 |
| `test_retrieve_full_integration` | ファイル読み込み統合 | 統合 |
| `test_parser_mode_switching` | モード切り替え | 単体 |
| `test_parser_empty_lines_and_comments` | 空行・コメント処理 | 単体 |
| `test_field_parsing_edge_cases` | フィールド解析エッジケース | 単体 |
| `test_unmapped_instances` | マッピングされていないインスタンス | 単体 |
| `test_file_encoding_with_bom` | UTF-8 BOMファイル処理 | 単体 |

### 選択可能定義パーサー (`tests/definitions/test_selectable.py`)
| テスト名 | 内容 | カテゴリ |
|---------|------|----------|
| `test_retrieve_basic_functionality` | 基本機能 | 単体 |
| `test_table_structure` | テーブル構造 | 単体 |
| `test_multiple_items` | 複数アイテム処理 | 単体 |
| `test_empty_items` | 空アイテム処理 | 単体 |
| `test_single_item` | 単一アイテム処理 | 単体 |
| `test_special_characters_in_names` | 特殊文字対応 | 単体 |
| `test_prefix_variations` | プレフィックスバリエーション | 単体 |
| `test_field_properties_detailed` | フィールドプロパティ詳細 | 単体 |
| `test_consistency_across_tables` | テーブル間一貫性 | 単体 |

## 🎯 今後の拡張方針

### 新機能追加時のテスト要件
1. **新しい定義パーサー追加時**
   - 基本的な解析機能のテスト
   - エラーハンドリングのテスト
   - エッジケースのテスト
   - 統合テストの追加

2. **データベース対応追加時**
   - 接続テスト（モックと実機）
   - スキーマ情報取得テスト
   - 特有機能のテスト

3. **パフォーマンス改善時**
   - ベンチマークテストの追加
   - メモリ使用量のモニタリング
   - 大容量データでの検証

このような管理により、コードの品質を継続的に保ち、リグレッション（機能の退化）を防ぎ、新機能の安全な追加が可能になります。