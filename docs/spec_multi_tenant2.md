# DBGear マルチテナント対応 詳細設計書 v2

## 概要

DBGearのマルチテナント機能は、1つの顧客環境内で数百のテナント用データベースを効率的に管理するためのシステムです。テンプレートベースの設定とYAMLレジストリによる一括管理により、手作業でのフォルダ・ファイル管理を排除します。

### 設計目標

- **テンプレート活用**: 複数のテナントタイプに対応した柔軟なテンプレートシステム
- **一括管理**: tenant_registry.yamlを起点とした集中管理
- **混在対応**: テナント型・固定名・共通DBの混在環境
- **スケーラビリティ**: 顧客内数百テナントの自動プロビジョニング
- **変数置換**: 柔軟な名前・設定の動的生成

## アーキテクチャ概要

### フォルダ構造設計

```
customer_a/                          # 顧客Aフォルダ（手作業管理・数十レベル）
├── environ.yaml                     # 顧客A環境設定
├── tenant_registry.yaml             # 🎯 マルチテナント定義・操作起点
├── tenant_type1/                    # SaaS標準版テンプレート
│   ├── _mapping.yaml               # 環境マッピング定義
│   ├── main@users.dat              # 初期データ
│   ├── main@orders.dat
│   └── main@products.dat
├── tenant_type2/                    # エンタープライズ版テンプレート
│   ├── _mapping.yaml
│   ├── main@users.dat
│   ├── main@orders.dat
│   ├── main@audit_logs.dat         # 追加機能
│   └── main@enterprise_features.dat
├── common/                          # 共通データベース用
│   ├── _mapping.yaml
│   ├── shared@system_config.dat
│   └── shared@global_settings.dat
└── analytics_db/                    # 分析用固定DB
    ├── _mapping.yaml
    ├── analytics@metrics.dat
    └── analytics@reports.dat

customer_b/                          # 顧客Bフォルダ（手作業管理・数十レベル）
├── environ.yaml
├── tenant_registry.yaml
├── tenant_type1/
└── ...
```

### 実行時データベース生成結果

```
MySQL/PostgreSQL Database Level:
├── customer_a_tenant_001_main       # テナント型DB (tenant_type1ベース)
├── customer_a_tenant_002_main
├── ...
├── customer_a_tenant_100_main
├── customer_a_ent_001_main          # エンタープライズテナント (tenant_type2ベース)
├── customer_a_ent_002_main  
├── ...
├── customer_a_ent_050_main
├── customer_a_analytics             # 固定名DB (analytics_dbベース)
├── customer_a_common                # 共通DB (commonベース)
└── customer_a_logs                  # ログDB (commonベース)
```

## コア設計: tenant_registry.yaml

### 基本構造

```yaml
# customer_a/tenant_registry.yaml
registry_version: "2.0"
customer_info:
  customer_code: "customer_a"
  customer_name: "Customer A Corporation"
  region: "japan"
  environment: "production"
  
# データベース群定義
database_groups:
  # === テナント型データベース群 ===
  saas_standard_tenants:
    type: "tenant_group"             # tenant_group | fixed_group
    template: "tenant_type1"         # ベーステンプレートフォルダ
    tenant_count: 100                # 作成するテナント数
    tenant_id_start: 1               # 開始番号
    tenant_id_format: "{:03d}"       # 001, 002, 003... 形式
    
    # データベース命名規則
    naming_pattern: "{customer_code}_tenant_{tenant_id}_main"
    
    # 変数置換定義
    variables:
      TENANT_PREFIX: "{customer_code}_tenant_{tenant_id}"
      CUSTOMER_CODE: "{customer_code}"
      TENANT_TYPE: "standard"
      DATABASE_NAME: "{customer_code}_tenant_{tenant_id}_main"
      
    # 運用設定
    auto_provision: true
    backup_enabled: true
    monitoring_enabled: true
    
  # === エンタープライズテナント群 ===  
  enterprise_tenants:
    type: "tenant_group"
    template: "tenant_type2"
    tenant_count: 50
    tenant_id_start: 1
    tenant_id_format: "{:03d}"
    
    naming_pattern: "{customer_code}_ent_{tenant_id}_main"
    
    variables:
      TENANT_PREFIX: "{customer_code}_ent_{tenant_id}"
      CUSTOMER_CODE: "{customer_code}"
      TENANT_TYPE: "enterprise"
      DATABASE_NAME: "{customer_code}_ent_{tenant_id}_main"
      ENTERPRISE_FEATURES: "enabled"
      AUDIT_ENABLED: "true"
      
    auto_provision: true
    backup_enabled: true
    monitoring_enabled: true
    
  # === 固定名データベース群 ===
  fixed_databases:
    type: "fixed_group"
    databases:
      - name: "customer_a_analytics"
        template: "analytics_db"
        variables:
          ANALYTICS_DB: "customer_a_analytics"
          CUSTOMER_CODE: "{customer_code}"
          RETENTION_DAYS: "365"
          
      - name: "customer_a_common"  
        template: "common"
        variables:
          COMMON_DB: "customer_a_common"
          CUSTOMER_CODE: "{customer_code}"
          SHARED_CONFIG: "enabled"
          
      - name: "customer_a_logs"
        template: "common"  
        variables:
          LOG_DB: "customer_a_logs"
          CUSTOMER_CODE: "{customer_code}"
          LOG_RETENTION: "90"

# 全体運用設定
operations:
  batch_settings:
    max_parallel: 20               # 並列実行数
    timeout_seconds: 300           # タイムアウト
    retry_attempts: 3              # リトライ回数
    
  provisioning:
    auto_create_on_deploy: true    # デプロイ時自動作成
    validate_before_create: true   # 作成前検証
    backup_before_update: false    # 更新前バックアップ
    
  monitoring:
    health_check_interval: 300     # ヘルスチェック間隔（秒）
    metrics_collection: true      # メトリクス収集
    alert_thresholds:
      connection_usage: 80         # 接続使用率アラート閾値
      error_rate: 5                # エラー率アラート閾値（%）
      
# 環境固有設定
environment_config:
  database_defaults:
    charset: "utf8mb4"
    collation: "utf8mb4_unicode_ci"
    connection_pool_size: 10
    connection_timeout: 30
    
  security:
    tenant_isolation: "database"   # database | schema | table
    cross_tenant_access: false     # テナント間アクセス禁止
    audit_logging: true            # 監査ログ有効
```

### 拡張設定例

```yaml
# 段階的デプロイメント設定
deployment_strategy:
  type: "rolling"                  # rolling | blue_green | canary
  batch_size: 10                   # 一度に処理する数
  wait_between_batches: 30         # バッチ間待機時間（秒）
  
  # カナリアデプロイメント
  canary:
    initial_percentage: 5          # 初期展開率
    increment_percentage: 25       # 段階的増加率
    evaluation_period: 300         # 評価期間（秒）
    
# データマイグレーション設定
migration_config:
  schema_version_tracking: true    # スキーマバージョン管理
  data_migration_scripts: "./migrations/"
  rollback_enabled: true          # ロールバック機能
  
# カスタムフック
hooks:
  pre_provision: ["./scripts/pre_provision.sh"]
  post_provision: ["./scripts/post_provision.sh", "./scripts/notify_admin.py"]
  pre_update: ["./scripts/backup_data.sh"]
  post_update: ["./scripts/validate_update.py"]
```

## テンプレートシステム設計

### テンプレートフォルダ構造

```
tenant_type1/                       # SaaS標準版テンプレート
├── _mapping.yaml                   # 環境マッピング（変数置換対象）
├── main@users.dat                  # 初期データ（変数置換対象）
├── main@orders.dat
├── main@products.dat
├── main@settings.dat
└── README.md                       # テンプレート説明

tenant_type2/                       # エンタープライズ版テンプレート  
├── _mapping.yaml
├── main@users.dat
├── main@orders.dat
├── main@products.dat
├── main@settings.dat
├── main@audit_logs.dat             # エンタープライズ固有
├── main@enterprise_features.dat   # エンタープライズ固有
├── main@compliance_data.dat       # エンタープライズ固有
└── README.md
```

### 変数置換システム

#### テンプレート例: `tenant_type1/_mapping.yaml`

```yaml
# tenant_type1/_mapping.yaml
group: "main"
base: "common"
instances:
  - "main"
description: "SaaS標準テナント: {TENANT_PREFIX}"

deployment: true

# データベース接続設定（変数置換）
database_config:
  main:
    database_name: "{DATABASE_NAME}"
    connection_pool_size: 10
    
# テナント固有設定
tenant_config:
  tenant_id: "{TENANT_PREFIX}"
  tenant_type: "{TENANT_TYPE}"
  customer_code: "{CUSTOMER_CODE}"
  
# データモデル設定  
data_models:
  users:
    table_name: "users"
    tenant_isolation_column: "tenant_id"
    default_tenant_value: "{TENANT_PREFIX}"
    
  orders:
    table_name: "orders" 
    tenant_isolation_column: "tenant_id"
    default_tenant_value: "{TENANT_PREFIX}"
```

#### 初期データ例: `tenant_type1/main@users.dat`

```yaml
# tenant_type1/main@users.dat
- id: 1
  username: "admin"
  email: "admin@{CUSTOMER_CODE}.example.com"
  tenant_id: "{TENANT_PREFIX}"
  role: "admin"
  created_at: "2024-01-01T00:00:00Z"
  
- id: 2  
  username: "operator"
  email: "operator@{CUSTOMER_CODE}.example.com"
  tenant_id: "{TENANT_PREFIX}"
  role: "operator" 
  created_at: "2024-01-01T00:00:00Z"
  
- id: 3
  username: "user001"
  email: "user001@{CUSTOMER_CODE}.example.com"
  tenant_id: "{TENANT_PREFIX}"
  role: "user"
  created_at: "2024-01-01T00:00:00Z"
```

#### エンタープライズテンプレート例: `tenant_type2/_mapping.yaml`

```yaml
# tenant_type2/_mapping.yaml  
group: "main"
base: "common"
instances:
  - "main"
description: "エンタープライズテナント: {TENANT_PREFIX}"

deployment: true

# 拡張データベース設定
database_config:
  main:
    database_name: "{DATABASE_NAME}"
    connection_pool_size: 20        # より大きなプール
    
# エンタープライズ固有設定
enterprise_config:
  audit_enabled: "{AUDIT_ENABLED}"
  compliance_mode: "strict"
  backup_frequency: "hourly"
  retention_policy: "7years"
  
# 拡張データモデル
data_models:
  users:
    table_name: "users"
    tenant_isolation_column: "tenant_id"
    default_tenant_value: "{TENANT_PREFIX}"
    audit_enabled: true
    
  audit_logs:
    table_name: "audit_logs"
    tenant_isolation_column: "tenant_id"  
    default_tenant_value: "{TENANT_PREFIX}"
    retention_days: 2555  # 7年
    
  enterprise_features:
    table_name: "enterprise_features"
    tenant_isolation_column: "tenant_id"
    default_tenant_value: "{TENANT_PREFIX}"
```

## 実装コンポーネント設計

### 1. Registry Manager

```python
# packages/dbgear/dbgear/models/multi_tenant/registry_manager.py
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml

class TenantRegistry:
    """tenant_registry.yaml管理クラス"""
    
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.config = self._load_registry()
        
    def _load_registry(self) -> Dict[str, Any]:
        """レジストリファイル読み込み"""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def get_database_groups(self) -> Dict[str, Any]:
        """データベースグループ定義取得"""
        return self.config.get('database_groups', {})
        
    def get_tenant_groups(self) -> Dict[str, Any]:
        """テナント型グループのみ取得"""
        groups = self.get_database_groups()
        return {k: v for k, v in groups.items() 
                if v.get('type') == 'tenant_group'}
                
    def get_fixed_groups(self) -> Dict[str, Any]:
        """固定名グループのみ取得"""
        groups = self.get_database_groups()
        return {k: v for k, v in groups.items() 
                if v.get('type') == 'fixed_group'}
                
    def get_customer_info(self) -> Dict[str, str]:
        """顧客情報取得"""
        return self.config.get('customer_info', {})
        
    def get_operations_config(self) -> Dict[str, Any]:
        """運用設定取得"""
        return self.config.get('operations', {})

class DatabaseDefinitionGenerator:
    """データベース定義生成クラス"""
    
    def __init__(self, registry: TenantRegistry):
        self.registry = registry
        
    def generate_tenant_definitions(self, group_name: str) -> List[Dict[str, Any]]:
        """テナントグループからDB定義一覧生成"""
        groups = self.registry.get_tenant_groups()
        if group_name not in groups:
            raise ValueError(f"Tenant group '{group_name}' not found")
            
        group_config = groups[group_name]
        definitions = []
        
        # テナントID生成
        start_id = group_config.get('tenant_id_start', 1)
        count = group_config.get('tenant_count', 0)
        id_format = group_config.get('tenant_id_format', '{:03d}')
        
        for i in range(count):
            tenant_id = id_format.format(start_id + i)
            
            # 変数置換コンテキスト作成
            context = self._create_variable_context(group_config, tenant_id)
            
            # データベース定義生成
            definition = {
                'database_name': self._substitute_variables(
                    group_config['naming_pattern'], context
                ),
                'tenant_id': tenant_id,
                'template': group_config['template'],
                'variables': context,
                'group_name': group_name
            }
            definitions.append(definition)
            
        return definitions
        
    def generate_fixed_definitions(self, group_name: str) -> List[Dict[str, Any]]:
        """固定名グループからDB定義一覧生成"""
        groups = self.registry.get_fixed_groups()
        if group_name not in groups:
            raise ValueError(f"Fixed group '{group_name}' not found")
            
        group_config = groups[group_name]
        definitions = []
        
        for db_config in group_config.get('databases', []):
            # 変数置換コンテキスト作成
            context = self._create_variable_context(db_config)
            
            definition = {
                'database_name': db_config['name'],
                'template': db_config['template'],
                'variables': context,
                'group_name': group_name
            }
            definitions.append(definition)
            
        return definitions
        
    def _create_variable_context(self, config: Dict[str, Any], tenant_id: str = None) -> Dict[str, str]:
        """変数置換用コンテキスト作成"""
        customer_info = self.registry.get_customer_info()
        context = customer_info.copy()
        
        if tenant_id:
            context['tenant_id'] = tenant_id
            
        # 設定からの変数をマージ
        variables = config.get('variables', {})
        for key, value in variables.items():
            context[key] = self._substitute_variables(value, context)
            
        return context
        
    def _substitute_variables(self, template: str, context: Dict[str, str]) -> str:
        """変数置換実行"""
        result = template
        for key, value in context.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result
```

### 2. Template Processor

```python
# packages/dbgear/dbgear/models/multi_tenant/template_processor.py
from pathlib import Path
import yaml
import re
from typing import Dict, Any, List

class TemplateProcessor:
    """テンプレート処理クラス"""
    
    def __init__(self, customer_path: str):
        self.customer_path = Path(customer_path)
        
    def process_template(self, template_name: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """テンプレートを変数置換して処理"""
        template_path = self.customer_path / template_name
        
        if not template_path.exists():
            raise ValueError(f"Template '{template_name}' not found at {template_path}")
            
        result = {
            'mapping': self._process_mapping_file(template_path, variables),
            'data_files': self._process_data_files(template_path, variables)
        }
        
        return result
        
    def _process_mapping_file(self, template_path: Path, variables: Dict[str, str]) -> Dict[str, Any]:
        """_mapping.yamlファイルの変数置換処理"""
        mapping_file = template_path / '_mapping.yaml'
        
        if not mapping_file.exists():
            raise ValueError(f"Mapping file not found: {mapping_file}")
            
        # ファイル読み込み
        with open(mapping_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 変数置換
        substituted_content = self._substitute_variables_in_text(content, variables)
        
        # YAML解析
        return yaml.safe_load(substituted_content)
        
    def _process_data_files(self, template_path: Path, variables: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """データファイル群の変数置換処理"""
        data_files = {}
        
        # .datファイルを検索
        for data_file in template_path.glob('*.dat'):
            file_key = data_file.stem  # main@users.dat -> main@users
            
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 変数置換
            substituted_content = self._substitute_variables_in_text(content, variables)
            
            # YAML解析
            try:
                data_files[file_key] = yaml.safe_load(substituted_content) or []
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {data_file}: {e}")
                
        return data_files
        
    def _substitute_variables_in_text(self, text: str, variables: Dict[str, str]) -> str:
        """テキスト内の変数置換"""
        result = text
        
        # {VARIABLE_NAME} 形式の置換
        for key, value in variables.items():
            pattern = f'{{{key}}}'
            result = result.replace(pattern, str(value))
            
        return result
        
    def validate_template(self, template_name: str) -> List[str]:
        """テンプレート構造検証"""
        template_path = self.customer_path / template_name
        issues = []
        
        if not template_path.exists():
            issues.append(f"Template directory not found: {template_path}")
            return issues
            
        # _mapping.yaml存在確認
        mapping_file = template_path / '_mapping.yaml'
        if not mapping_file.exists():
            issues.append(f"Missing _mapping.yaml in {template_path}")
            
        # データファイル存在確認
        data_files = list(template_path.glob('*.dat'))
        if not data_files:
            issues.append(f"No data files (*.dat) found in {template_path}")
            
        return issues
```

### 3. Provisioning Engine

```python
# packages/dbgear/dbgear/models/multi_tenant/provisioning_engine.py
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ProvisioningStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"

@dataclass
class ProvisioningResult:
    database_name: str
    status: ProvisioningStatus
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class MultiTenantProvisioningEngine:
    """マルチテナントプロビジョニングエンジン"""
    
    def __init__(self, 
                 registry: TenantRegistry,
                 template_processor: TemplateProcessor,
                 db_manager: 'DatabaseManager'):
        self.registry = registry
        self.template_processor = template_processor
        self.db_manager = db_manager
        
    async def deploy_all_groups(self, dry_run: bool = True) -> List[ProvisioningResult]:
        """全グループ一括デプロイ"""
        results = []
        
        # テナントグループ処理
        tenant_groups = self.registry.get_tenant_groups()
        for group_name in tenant_groups.keys():
            group_results = await self.deploy_tenant_group(group_name, dry_run)
            results.extend(group_results)
            
        # 固定名グループ処理
        fixed_groups = self.registry.get_fixed_groups()
        for group_name in fixed_groups.keys():
            group_results = await self.deploy_fixed_group(group_name, dry_run)
            results.extend(group_results)
            
        return results
        
    async def deploy_tenant_group(self, group_name: str, dry_run: bool = True) -> List[ProvisioningResult]:
        """テナントグループデプロイ"""
        generator = DatabaseDefinitionGenerator(self.registry)
        definitions = generator.generate_tenant_definitions(group_name)
        
        # 並列実行設定
        operations_config = self.registry.get_operations_config()
        max_parallel = operations_config.get('batch_settings', {}).get('max_parallel', 10)
        
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def deploy_single_database(definition):
            async with semaphore:
                return await self._deploy_single_database(definition, dry_run)
                
        # 並列実行
        tasks = [deploy_single_database(definition) for definition in definitions]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def deploy_fixed_group(self, group_name: str, dry_run: bool = True) -> List[ProvisioningResult]:
        """固定名グループデプロイ"""
        generator = DatabaseDefinitionGenerator(self.registry)
        definitions = generator.generate_fixed_definitions(group_name)
        
        results = []
        for definition in definitions:
            result = await self._deploy_single_database(definition, dry_run)
            results.append(result)
            
        return results
        
    async def _deploy_single_database(self, definition: Dict[str, Any], dry_run: bool) -> ProvisioningResult:
        """単一データベースデプロイ"""
        import time
        start_time = time.time()
        
        database_name = definition['database_name']
        
        try:
            # テンプレート処理
            processed_template = self.template_processor.process_template(
                definition['template'],
                definition['variables']
            )
            
            if not dry_run:
                # データベース作成
                await self.db_manager.create_database(database_name)
                
                # スキーマ適用
                await self.db_manager.apply_schema(database_name, processed_template['mapping'])
                
                # 初期データ投入
                await self.db_manager.load_initial_data(database_name, processed_template['data_files'])
                
            return ProvisioningResult(
                database_name=database_name,
                status=ProvisioningStatus.SUCCESS,
                duration=time.time() - start_time,
                details={
                    'template': definition['template'],
                    'group': definition['group_name'],
                    'dry_run': dry_run
                }
            )
            
        except Exception as e:
            return ProvisioningResult(
                database_name=database_name,
                status=ProvisioningStatus.ERROR,
                duration=time.time() - start_time,
                error=str(e)
            )
```

## CLI設計

### コマンド体系

```python
# packages/dbgear/dbgear/cli/multi_tenant_v2.py
import click
import asyncio
import yaml
from tabulate import tabulate

@click.group("multi-tenant")
def multi_tenant_cli():
    """マルチテナント管理コマンド"""
    pass

@multi_tenant_cli.command("deploy")
@click.option("--registry", required=True, help="tenant_registry.yamlパス")
@click.option("--group", help="特定グループのみデプロイ")
@click.option("--dry-run", is_flag=True, help="実際のデプロイは行わない")
@click.option("--parallel", type=int, help="並列実行数（設定上書き）")
def deploy_command(registry: str, group: str, dry_run: bool, parallel: int):
    """tenant_registry.yamlを起点に全DB作成"""
    async def _deploy():
        # レジストリ読み込み
        tenant_registry = TenantRegistry(registry)
        template_processor = TemplateProcessor(Path(registry).parent)
        provisioning_engine = MultiTenantProvisioningEngine(
            tenant_registry, template_processor, get_db_manager()
        )
        
        if group:
            # 特定グループのみ
            if group in tenant_registry.get_tenant_groups():
                results = await provisioning_engine.deploy_tenant_group(group, dry_run)
            elif group in tenant_registry.get_fixed_groups():
                results = await provisioning_engine.deploy_fixed_group(group, dry_run)
            else:
                click.echo(f"Group '{group}' not found", err=True)
                return
        else:
            # 全グループ
            results = await provisioning_engine.deploy_all_groups(dry_run)
            
        # 結果表示
        display_provisioning_results(results, dry_run)
        
    asyncio.run(_deploy())

@multi_tenant_cli.command("preview")
@click.option("--registry", required=True, help="tenant_registry.yamlパス")
@click.option("--group", help="特定グループのみプレビュー")
@click.option("--limit", type=int, default=5, help="表示件数制限")
def preview_command(registry: str, group: str, limit: int):
    """設定プレビュー表示"""
    tenant_registry = TenantRegistry(registry)
    generator = DatabaseDefinitionGenerator(tenant_registry)
    
    if group:
        if group in tenant_registry.get_tenant_groups():
            definitions = generator.generate_tenant_definitions(group)
        elif group in tenant_registry.get_fixed_groups():
            definitions = generator.generate_fixed_definitions(group)
        else:
            click.echo(f"Group '{group}' not found", err=True)
            return
    else:
        definitions = []
        # 全グループの定義取得
        for group_name in tenant_registry.get_tenant_groups():
            definitions.extend(generator.generate_tenant_definitions(group_name))
        for group_name in tenant_registry.get_fixed_groups():
            definitions.extend(generator.generate_fixed_definitions(group_name))
    
    # 制限適用
    limited_definitions = definitions[:limit]
    
    # テーブル表示
    table_data = []
    for definition in limited_definitions:
        table_data.append([
            definition['database_name'],
            definition['template'],
            definition.get('group_name', 'N/A'),
            definition.get('tenant_id', 'N/A')
        ])
        
    headers = ['Database Name', 'Template', 'Group', 'Tenant ID']
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    if len(definitions) > limit:
        click.echo(f"\n... and {len(definitions) - limit} more databases")

@multi_tenant_cli.command("add-tenants")
@click.option("--registry", required=True, help="tenant_registry.yamlパス")
@click.option("--group", required=True, help="対象テナントグループ")
@click.option("--count", type=int, required=True, help="追加するテナント数")
@click.option("--dry-run", is_flag=True, help="実際の追加は行わない")
def add_tenants_command(registry: str, group: str, count: int, dry_run: bool):
    """既存グループにテナント追加"""
    # レジストリ読み込み・更新
    with open(registry, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    if group not in config.get('database_groups', {}):
        click.echo(f"Group '{group}' not found", err=True)
        return
        
    current_count = config['database_groups'][group].get('tenant_count', 0)
    new_count = current_count + count
    
    if dry_run:
        click.echo(f"Would add {count} tenants to group '{group}' (current: {current_count}, new total: {new_count})")
        return
        
    # 設定更新
    config['database_groups'][group]['tenant_count'] = new_count
    
    with open(registry, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
        
    click.echo(f"Added {count} tenants to group '{group}'. New total: {new_count}")
    click.echo("Run 'dbgear multi-tenant deploy' to provision new tenants.")

@multi_tenant_cli.command("healthcheck")
@click.option("--registry", required=True, help="tenant_registry.yamlパス")
@click.option("--group", help="特定グループのみチェック")
@click.option("--parallel", type=int, default=20, help="並列実行数")
@click.option("--report", help="レポート出力ファイル")
def healthcheck_command(registry: str, group: str, parallel: int, report: str):
    """一括ヘルスチェック"""
    async def _healthcheck():
        tenant_registry = TenantRegistry(registry)
        generator = DatabaseDefinitionGenerator(tenant_registry)
        
        # 対象データベース取得
        if group:
            if group in tenant_registry.get_tenant_groups():
                definitions = generator.generate_tenant_definitions(group)
            elif group in tenant_registry.get_fixed_groups():
                definitions = generator.generate_fixed_definitions(group)
            else:
                click.echo(f"Group '{group}' not found", err=True)
                return
        else:
            definitions = []
            for group_name in tenant_registry.get_tenant_groups():
                definitions.extend(generator.generate_tenant_definitions(group_name))
            for group_name in tenant_registry.get_fixed_groups():
                definitions.extend(generator.generate_fixed_definitions(group_name))
        
        # 並列ヘルスチェック実行
        semaphore = asyncio.Semaphore(parallel)
        
        async def check_single_database(definition):
            async with semaphore:
                return await perform_health_check(definition['database_name'])
                
        tasks = [check_single_database(definition) for definition in definitions]
        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果集計・表示
        healthy_count = sum(1 for result in health_results if result.get('healthy', False))
        total_count = len(health_results)
        
        click.echo(f"Health Check Results: {healthy_count}/{total_count} healthy")
        
        # レポート出力
        if report:
            with open(report, 'w') as f:
                yaml.safe_dump({
                    'timestamp': datetime.now().isoformat(),
                    'summary': {
                        'total': total_count,
                        'healthy': healthy_count,
                        'unhealthy': total_count - healthy_count
                    },
                    'details': health_results
                }, f)
            click.echo(f"Report saved to {report}")
            
    asyncio.run(_healthcheck())

@multi_tenant_cli.command("validate")
@click.option("--registry", required=True, help="tenant_registry.yamlパス")
def validate_command(registry: str):
    """tenant_registry.yamlとテンプレート構造検証"""
    try:
        # レジストリ検証
        tenant_registry = TenantRegistry(registry)
        template_processor = TemplateProcessor(Path(registry).parent)
        
        issues = []
        
        # テンプレート存在確認
        all_groups = {**tenant_registry.get_tenant_groups(), **tenant_registry.get_fixed_groups()}
        
        for group_name, group_config in all_groups.items():
            if group_config.get('type') == 'tenant_group':
                template_name = group_config.get('template')
                template_issues = template_processor.validate_template(template_name)
                if template_issues:
                    issues.extend([f"Group '{group_name}': {issue}" for issue in template_issues])
            elif group_config.get('type') == 'fixed_group':
                for db_config in group_config.get('databases', []):
                    template_name = db_config.get('template')
                    template_issues = template_processor.validate_template(template_name)
                    if template_issues:
                        issues.extend([f"Group '{group_name}', DB '{db_config['name']}': {issue}" for issue in template_issues])
        
        if issues:
            click.echo("Validation Issues Found:")
            for issue in issues:
                click.echo(f"  ❌ {issue}")
        else:
            click.echo("✅ Validation passed. Registry and templates are valid.")
            
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)

def display_provisioning_results(results: List[ProvisioningResult], dry_run: bool):
    """プロビジョニング結果表示"""
    success_count = sum(1 for r in results if r.status == ProvisioningStatus.SUCCESS)
    error_count = sum(1 for r in results if r.status == ProvisioningStatus.ERROR)
    
    mode = "DRY RUN" if dry_run else "ACTUAL"
    click.echo(f"\n{mode} Results: {success_count} success, {error_count} errors")
    
    if error_count > 0:
        click.echo("\nErrors:")
        for result in results:
            if result.status == ProvisioningStatus.ERROR:
                click.echo(f"  ❌ {result.database_name}: {result.error}")
                
    # 成功例も数件表示
    success_results = [r for r in results if r.status == ProvisioningStatus.SUCCESS]
    if success_results:
        click.echo(f"\nFirst 5 successful databases:")
        for result in success_results[:5]:
            click.echo(f"  ✅ {result.database_name} ({result.duration:.2f}s)")

# メインCLIに登録
def register_multi_tenant_commands(cli):
    cli.add_command(multi_tenant_cli)
```

## 使用例

### 基本的な運用フロー

```bash
cd customer_a/

# 1. 設定検証
dbgear multi-tenant validate --registry tenant_registry.yaml

# 2. プレビュー確認
dbgear multi-tenant preview --registry tenant_registry.yaml --limit 10

# 3. ドライラン実行
dbgear multi-tenant deploy --registry tenant_registry.yaml --dry-run

# 4. 実際のデプロイ（全グループ）
dbgear multi-tenant deploy --registry tenant_registry.yaml

# 5. 特定グループのみデプロイ
dbgear multi-tenant deploy --registry tenant_registry.yaml --group saas_standard_tenants

# 6. テナント追加
dbgear multi-tenant add-tenants --registry tenant_registry.yaml --group saas_standard_tenants --count 20

# 7. ヘルスチェック
dbgear multi-tenant healthcheck --registry tenant_registry.yaml --parallel 30 --report health_report.yaml
```

### 開発・テスト環境での使用

```bash
# 小規模テスト環境
dbgear multi-tenant deploy --registry tenant_registry_dev.yaml --group saas_standard_tenants --dry-run

# 特定テンプレートのみテスト
dbgear multi-tenant preview --registry tenant_registry.yaml --group enterprise_tenants --limit 3
```

## まとめ

### この設計の特徴

1. **集中管理**: tenant_registry.yamlが全ての起点
2. **テンプレート活用**: 複数のテナントタイプに柔軟対応
3. **混在対応**: テナント型・固定名・共通DBの統一管理
4. **スケーラビリティ**: 数百テナントの並列プロビジョニング
5. **運用性**: バリデーション・プレビュー・ヘルスチェック完備

### 導入効果

- **手作業排除**: フォルダ・ファイル管理の完全自動化
- **一貫性保証**: テンプレートベースによる設定統一
- **運用効率**: 一括操作・監視・メンテナンス機能
- **拡張性**: 新しいテナントタイプの容易な追加

この設計により、顧客環境内での大規模マルチテナント運用が効率的に実現できます。