# DBGear マルチテナント対応 詳細設計書

## 概要

DBGearは数十〜数百レベルのマルチテナント環境に対応するため、従来のYAMLファイルベース管理から外部データソース統合・動的設定生成・大規模運用自動化アーキテクチャへ拡張します。

### 設計目標

- **スケーラビリティ**: 数百テナントの同時管理
- **自動化**: 手作業でのYAML管理完全排除
- **柔軟性**: 複数の外部データソース対応
- **運用性**: バッチ処理・監視・災害復旧機能
- **プログラマビリティ**: API・SDK・CI/CD統合

## アーキテクチャ概要

### 従来アーキテクチャの課題

1. **静的YAML管理**: 数百ファイルの手動管理が破綻
2. **スケーラビリティ限界**: ファイルシステムベースの性能限界
3. **運用自動化不足**: プロビジョニング・デプロビジョニングが手作業
4. **外部システム連携困難**: CRM・課金システム等との同期不可

### 新アーキテクチャ設計

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Data Sources                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Database      │      API        │         CSV/Excel           │
│  (PostgreSQL/   │   (REST/GraphQL)│      (File-based)           │
│   MySQL/etc)    │                 │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Tenant Registry Provider Layer                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│DatabaseProvider │   APIProvider   │       CSVProvider           │
│                 │                 │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                Template Engine + Macro System                   │
├─────────────────────────────────────────────────────────────────┤
│  • Jinja2 Template Processing                                   │
│  • Dynamic Configuration Generation                             │
│  • Name Substitution & Macro Expansion                         │
│  • Schema Instantiation                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Tenant Automation Engine                           │
├─────────────────────────────────────────────────────────────────┤
│  • Bulk Provisioning (Async/Parallel)                          │
│  • Schema Migration & Deployment                               │
│  • Health Check & Monitoring                                   │
│  • Backup & Disaster Recovery                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API & CLI Interface                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   REST API      │   Python SDK    │      CLI Commands           │
│                 │                 │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

## コンポーネント詳細設計

### 1. Tenant Registry Provider Layer

#### 1.1 抽象基底クラス

```python
# packages/dbgear/dbgear/models/multi_tenant/tenant_registry.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class TenantInfo(BaseModel):
    """テナント基本情報"""
    tenant_id: str
    customer_name: str
    customer_code: str
    region: str
    tier: str  # basic/standard/premium/enterprise
    status: str  # active/inactive/suspended/terminated
    created_at: datetime
    updated_at: datetime
    
    # 分離戦略設定
    isolation_strategy: str  # database/schema/table
    database_prefix: Optional[str] = None
    schema_suffix: Optional[str] = None
    table_prefix: Optional[str] = None
    
    # インスタンス設定
    instances: List[str] = ["main"]  # main, test, staging etc.
    
    # 課金・契約情報
    billing_info: Optional[Dict[str, Any]] = None
    contract_info: Optional[Dict[str, Any]] = None

class TenantRegistryProvider(ABC):
    """テナント情報プロバイダーの抽象基底クラス"""
    
    @abstractmethod
    async def list_tenants(self, 
                          filters: Optional[Dict] = None, 
                          offset: int = 0, 
                          limit: int = 100) -> List[TenantInfo]:
        """テナント一覧取得（ページング対応）"""
        pass
        
    @abstractmethod
    async def get_tenant(self, tenant_id: str) -> TenantInfo:
        """個別テナント情報取得"""
        pass
        
    @abstractmethod
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """テナント固有設定取得"""
        pass
        
    @abstractmethod
    async def search_tenants(self, query: str) -> List[TenantInfo]:
        """テナント検索（SQL-like query support）"""
        pass
        
    @abstractmethod
    async def get_tenant_count(self, filters: Optional[Dict] = None) -> int:
        """条件に合致するテナント数取得"""
        pass
```

#### 1.2 Database Provider実装

```python
# packages/dbgear/dbgear/models/multi_tenant/providers/database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from cachetools import TTLCache

class DatabaseTenantProvider(TenantRegistryProvider):
    """データベースベーステナント管理"""
    
    def __init__(self, 
                 db_url: str, 
                 tenant_table: str = "tenants",
                 config_table: str = "tenant_configs",
                 cache_ttl: int = 300):
        self.engine = create_async_engine(db_url)
        self.tenant_table = tenant_table
        self.config_table = config_table
        self.cache = TTLCache(maxsize=1000, ttl=cache_ttl)
        
    async def list_tenants(self, 
                          filters: Optional[Dict] = None, 
                          offset: int = 0, 
                          limit: int = 100) -> List[TenantInfo]:
        """ページング対応テナント一覧取得"""
        async with self.engine.begin() as conn:
            query = select(self.tenant_table)
            
            # フィルター条件適用
            if filters:
                for key, value in filters.items():
                    if hasattr(self.tenant_table.c, key):
                        query = query.where(getattr(self.tenant_table.c, key) == value)
                        
            # ページング
            query = query.offset(offset).limit(limit)
            
            result = await conn.execute(query)
            rows = result.fetchall()
            
            return [TenantInfo(**row._asdict()) for row in rows]
            
    async def search_tenants(self, query: str) -> List[TenantInfo]:
        """SQL-likeクエリでテナント検索"""
        # 簡易SQL Parser実装または既存ライブラリ使用
        # 例: "region='asia' AND tier IN ('premium', 'enterprise')"
        parsed_query = self._parse_search_query(query)
        return await self.list_tenants(filters=parsed_query)
        
    def _parse_search_query(self, query: str) -> Dict[str, Any]:
        """検索クエリをDictに変換"""
        # 実装: シンプルなSQL-like parser
        # より高度な実装ではSQLAlchemyのtext()を使用
        pass
```

#### 1.3 API Provider実装

```python
# packages/dbgear/dbgear/models/multi_tenant/providers/api.py
import httpx
import asyncio

class APITenantProvider(TenantRegistryProvider):
    """REST APIベーステナント管理"""
    
    def __init__(self, 
                 api_base_url: str, 
                 auth_token: str,
                 timeout: int = 30,
                 retry_attempts: int = 3):
        self.client = httpx.AsyncClient(
            base_url=api_base_url,
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=timeout
        )
        self.retry_attempts = retry_attempts
        
    async def list_tenants(self, 
                          filters: Optional[Dict] = None, 
                          offset: int = 0, 
                          limit: int = 100) -> List[TenantInfo]:
        """API経由でテナント一覧取得"""
        params = {
            "offset": offset,
            "limit": limit
        }
        if filters:
            params.update(filters)
            
        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.get("/tenants", params=params)
                response.raise_for_status()
                
                data = response.json()
                return [TenantInfo(**item) for item in data["items"]]
                
            except httpx.RequestError as e:
                if attempt == self.retry_attempts - 1:
                    raise TenantRegistryError(f"API request failed: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """API経由でテナント設定取得"""
        response = await self.client.get(f"/tenants/{tenant_id}/config")
        response.raise_for_status()
        return response.json()
```

#### 1.4 CSV Provider実装

```python
# packages/dbgear/dbgear/models/multi_tenant/providers/csv.py
import csv
import io
from pathlib import Path
import aiofiles

class CSVTenantProvider(TenantRegistryProvider):
    """CSVファイルベーステナント管理"""
    
    def __init__(self, 
                 csv_path: str, 
                 config_dir: Optional[str] = None,
                 watch_changes: bool = True):
        self.csv_path = Path(csv_path)
        self.config_dir = Path(config_dir) if config_dir else None
        self.watch_changes = watch_changes
        self.last_modified = None
        self.cached_data = None
        
        if watch_changes:
            self._setup_file_watcher()
            
    async def list_tenants(self, 
                          filters: Optional[Dict] = None, 
                          offset: int = 0, 
                          limit: int = 100) -> List[TenantInfo]:
        """CSV読み込みでテナント一覧取得"""
        data = await self._load_csv_data()
        
        # フィルタリング
        if filters:
            filtered_data = []
            for row in data:
                match = True
                for key, value in filters.items():
                    if row.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_data.append(row)
            data = filtered_data
            
        # ページング
        paginated_data = data[offset:offset + limit]
        
        return [TenantInfo(**row) for row in paginated_data]
        
    async def _load_csv_data(self) -> List[Dict[str, Any]]:
        """CSV データ読み込み（キャッシュ対応）"""
        current_modified = self.csv_path.stat().st_mtime
        
        if (self.cached_data is None or 
            self.last_modified is None or 
            current_modified > self.last_modified):
            
            async with aiofiles.open(self.csv_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            # CSV parsing
            reader = csv.DictReader(io.StringIO(content))
            self.cached_data = list(reader)
            self.last_modified = current_modified
            
        return self.cached_data
```

### 2. Template Engine & Macro System

#### 2.1 Template Engine実装

```python
# packages/dbgear/dbgear/models/multi_tenant/template_engine.py
from jinja2 import Environment, FileSystemLoader
import yaml

class TenantTemplateEngine:
    """テンプレートベーステナント設定生成エンジン"""
    
    def __init__(self, 
                 template_dir: str, 
                 registry: TenantRegistryProvider,
                 cache_enabled: bool = True):
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.registry = registry
        self.cache_enabled = cache_enabled
        self.template_cache = {}
        
        # カスタムフィルター登録
        self._register_custom_filters()
        
    def _register_custom_filters(self):
        """カスタムJinja2フィルター登録"""
        self.template_env.filters.update({
            'tenant_prefix': self._filter_tenant_prefix,
            'db_name': self._filter_db_name,
            'schema_name': self._filter_schema_name,
            'table_name': self._filter_table_name,
            'safe_identifier': self._filter_safe_identifier,
        })
        
    def _filter_tenant_prefix(self, tenant_info: TenantInfo) -> str:
        """テナントプレフィックス生成"""
        return f"{tenant_info.customer_code}_{tenant_info.region}"
        
    def _filter_db_name(self, tenant_info: TenantInfo, instance: str) -> str:
        """データベース名生成"""
        prefix = self._filter_tenant_prefix(tenant_info)
        return f"{prefix}_{instance}"
        
    def _filter_table_name(self, tenant_info: TenantInfo, table: str) -> str:
        """テーブル名生成"""
        if tenant_info.table_prefix:
            return f"{tenant_info.table_prefix}{table}"
        return table
        
    async def generate_environment_config(self, tenant_id: str) -> Dict[str, Any]:
        """テナント用環境設定を動的生成"""
        tenant = await self.registry.get_tenant(tenant_id)
        config = await self.registry.get_tenant_config(tenant_id)
        
        template = self.template_env.get_template('environment.j2')
        rendered = template.render(
            tenant=tenant,
            config=config,
            instances=tenant.instances
        )
        
        return yaml.safe_load(rendered)
```

#### 2.2 Macro Processor実装

```python
# packages/dbgear/dbgear/models/multi_tenant/macro_processor.py
import re
from copy import deepcopy

class MacroProcessor:
    """名前置換マクロ処理システム"""
    
    def __init__(self, context: Dict[str, str]):
        self.context = context
        self.macro_functions = {
            'tenant_prefix': self._macro_tenant_prefix,
            'db_name': self._macro_db_name,
            'table_name': self._macro_table_name,
            'schema_name': self._macro_schema_name,
        }
        
    def process_schema_manager(self, schema_manager) -> 'SchemaManager':
        """SchemaManager内の名前をマクロ処理"""
        # ディープコピーで元データを保護
        processed_manager = deepcopy(schema_manager)
        
        # スキーマ名の処理
        new_schemas = {}
        for schema_name, schema in processed_manager.schemas.items():
            new_schema_name = self._process_string(schema_name)
            new_schemas[new_schema_name] = self._process_schema(schema)
            
        processed_manager.schemas = new_schemas
        return processed_manager
        
    def _process_string(self, value: str) -> str:
        """文字列のマクロ処理"""
        if not value:
            return value
            
        # ${MACRO_NAME} 形式のマクロを処理
        pattern = r'\$\{([A-Z_]+)\}'
        
        def replace_macro(match):
            macro_name = match.group(1).lower()
            if macro_name in self.context:
                return self.context[macro_name]
            return match.group(0)  # マクロが見つからない場合は元のまま
            
        result = re.sub(pattern, replace_macro, value)
        return result
        
    def _macro_tenant_prefix(self, args: str) -> str:
        return f"{self.context.get('customer_code', '')}_{self.context.get('region', '')}"
```

### 3. Tenant Automation Engine

```python
# packages/dbgear/dbgear/models/multi_tenant/automation_engine.py
import asyncio
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class OperationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
    ROLLBACK = "rollback"

@dataclass
class OperationResult:
    tenant_id: str
    operation: str
    status: OperationStatus
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class TenantAutomationEngine:
    """テナント運用自動化エンジン"""
    
    def __init__(self, 
                 registry: TenantRegistryProvider,
                 template_engine: TenantTemplateEngine,
                 max_parallel: int = 20,
                 operation_timeout: int = 300):
        self.registry = registry
        self.template_engine = template_engine
        self.max_parallel = max_parallel
        self.operation_timeout = operation_timeout
        self.operation_history: List[OperationResult] = []
        
    async def bulk_provision_tenants(self, 
                                   tenant_filters: Dict,
                                   dry_run: bool = True,
                                   parallel_limit: Optional[int] = None) -> List[OperationResult]:
        """大量テナント一括プロビジョニング"""
        start_time = time.time()
        
        # 対象テナント取得
        tenants = await self.registry.list_tenants(tenant_filters)
        
        if not tenants:
            return []
            
        parallel_limit = parallel_limit or min(self.max_parallel, len(tenants))
        
        # 並列実行セマフォ
        semaphore = asyncio.Semaphore(parallel_limit)
        
        async def provision_with_semaphore(tenant):
            async with semaphore:
                return await self._provision_single_tenant(tenant.tenant_id, dry_run)
                
        # 並列タスク実行
        tasks = [provision_with_semaphore(tenant) for tenant in tenants]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 例外ハンドリング
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(OperationResult(
                    tenant_id=tenants[i].tenant_id,
                    operation="provision",
                    status=OperationStatus.ERROR,
                    duration=time.time() - start_time,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
                
        self.operation_history.extend(processed_results)
        return processed_results
        
    async def _provision_single_tenant(self, tenant_id: str, dry_run: bool) -> OperationResult:
        """単一テナントプロビジョニング"""
        start_time = time.time()
        
        try:
            # 環境設定生成
            env_config = await self.template_engine.generate_environment_config(tenant_id)
            
            # dry_runでない場合のみ実際の処理
            if not dry_run:
                # データベース作成・スキーマ適用等の処理
                pass
                
            return OperationResult(
                tenant_id=tenant_id,
                operation="provision",
                status=OperationStatus.SUCCESS,
                duration=time.time() - start_time,
                details={"dry_run": dry_run}
            )
            
        except Exception as e:
            return OperationResult(
                tenant_id=tenant_id,
                operation="provision",
                status=OperationStatus.ERROR,
                duration=time.time() - start_time,
                error=str(e)
            )
```

### 4. CLI Commands

```python
# packages/dbgear/dbgear/cli/multi_tenant.py
import click
import asyncio
import json

@click.group("tenant")
def tenant_cli():
    """マルチテナント管理コマンド"""
    pass

@tenant_cli.command("sync")
@click.option("--source", required=True, help="データソース (crm/database/csv)")
@click.option("--dry-run", is_flag=True, help="実際の同期は行わない")
@click.option("--config", help="プロバイダー設定ファイル")
def sync_tenants(source: str, dry_run: bool, config: str):
    """外部システムからテナント情報同期"""
    async def _sync():
        # 実装: プロバイダー作成・同期処理
        click.echo(f"Syncing tenants from {source}")
        
    asyncio.run(_sync())

@tenant_cli.command("provision")
@click.option("--query", required=True, help="テナント選択クエリ")
@click.option("--parallel", default=10, help="並列実行数")
@click.option("--dry-run", is_flag=True, help="実際のプロビジョニングは行わない")
def provision_tenants(query: str, parallel: int, dry_run: bool):
    """テナント一括プロビジョニング"""
    async def _provision():
        # 実装: 自動化エンジン呼び出し
        click.echo(f"Provisioning tenants with query: {query}")
        
    asyncio.run(_provision())

@click.group("batch")
def batch_cli():
    """バッチ処理コマンド"""
    pass

@batch_cli.command("healthcheck")
@click.option("--parallel", default=50, help="並列実行数")
@click.option("--report", help="レポート出力ファイル")
def batch_health_check(parallel: int, report: str):
    """バッチヘルスチェック"""
    async def _healthcheck():
        # 実装: ヘルスチェック処理
        click.echo("Running health check on all tenants")
        
    asyncio.run(_healthcheck())
```

## テンプレート例

### Environment Template

```jinja2
<!-- templates/environment.j2 -->
name: "{{ tenant.tenant_id }}"
type: "tenant"
base: "{{ tenant.tier }}_base"

tenant_info:
  tenant_id: "{{ tenant.tenant_id }}"
  customer_name: "{{ tenant.customer_name }}"
  customer_code: "{{ tenant.customer_code }}"
  region: "{{ tenant.region }}"
  tier: "{{ tenant.tier }}"
  
# データベース設定
database_config:
{% for instance in tenant.instances %}
  {{ instance }}:
    database_name: "{{ tenant | tenant_prefix }}_{{ instance }}"
    schema_name: "{{ instance }}"
{% endfor %}

# 分離設定
isolation_config:
  strategy: "{{ tenant.isolation_strategy }}"
  naming_pattern: "{{ tenant | tenant_prefix }}_{instance}"
  
# マクロ定義
name_macros:
  database_prefix: "{{ tenant | tenant_prefix }}"
  table_prefix: "{{ tenant.table_prefix or '' }}"
```

### Schema Template

```jinja2
<!-- templates/schema.j2 -->
schemas:
  {{ tenant | tenant_prefix }}_main:
    tables:
      {{ tenant | table_name('users') }}:
        columns:
          - column_name: "id"
            column_type: "INT AUTO_INCREMENT"
            primary_key: true
          - column_name: "tenant_id"
            column_type: "VARCHAR(50)"
            nullable: false
            default_value: "'{{ tenant.tenant_id }}'"
          - column_name: "username"
            column_type: "VARCHAR(255)"
            nullable: false
            
        indexes:
          - index_name: "idx_tenant_id"
            columns: ["tenant_id"]
```

## 設定例

### project.yaml 拡張

```yaml
# マルチテナント設定
multi_tenant:
  enabled: true
  scale: "enterprise"
  
  # 外部データソース設定
  tenant_registry:
    provider: "database"
    config:
      database:
        url: "${TENANT_REGISTRY_DB_URL}"
        tenant_table: "tenants"
        cache_ttl: 300
        
  # テンプレート設定
  templates:
    base_dir: "./templates"
    schema_templates:
      - name: "saas_standard"
        file: "saas_standard_schema.j2"
      - name: "enterprise"  
        file: "enterprise_schema.j2"
        
  # 自動化設定
  automation:
    max_parallel_operations: 20
    operation_timeout: 300
    
  # 監視設定
  monitoring:
    enabled: true
    metrics_endpoint: "/metrics"
    log_level: "INFO"
```

## CLI使用例

### 基本的な運用フロー

```bash
# テナント情報同期
dbgear tenant sync --source crm --dry-run
dbgear tenant sync --source crm

# 新規テナントプロビジョニング
dbgear tenant provision \
  --query "status='active' AND tier='premium'" \
  --parallel 10

# バッチヘルスチェック
dbgear batch healthcheck --parallel 50 --report ./health_report.json

# スキーママイグレーション
dbgear batch deploy-schema \
  --migration ./migrations/v2.1.sql \
  --filter "tier IN ('premium', 'enterprise')"

# 監視・メトリクス
dbgear monitor status --dashboard
```

## パフォーマンス・スケーラビリティ対策

### 1. 接続プール最適化
- テナント別接続プール管理
- 動的プールサイズ調整
- 接続リーク検出・自動回復

### 2. キャッシュ戦略
- テナント情報のRedisキャッシュ
- スキーマ設定のメモリキャッシュ
- クエリ結果キャッシュ

### 3. 非同期処理
- 大量操作の非同期実行
- バックグラウンドタスク管理
- 進捗状況のリアルタイム更新

### 4. 監視・アラート
- テナント別パフォーマンス監視
- エラー率・レスポンス時間追跡
- 自動スケーリング対応

## まとめ

この詳細設計により、DBGearは数百レベルのマルチテナント環境に対応できます：

1. **外部データソース統合** - 手作業でのYAML管理を完全排除
2. **動的設定生成** - テンプレート + マクロによる柔軟な設定生成
3. **大規模運用自動化** - バッチ処理・並列実行・エラー処理
4. **プログラマブルAPI** - CI/CD・外部システム統合対応
5. **運用監視機能** - ヘルスチェック・メトリクス・アラート

段階的実装により、既存機能を維持しながらマルチテナント機能を追加できます。