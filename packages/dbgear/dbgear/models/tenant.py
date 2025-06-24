import pydantic
import yaml

from .base import BaseSchema
from .exceptions import DBGearEntityExistsError
from .exceptions import DBGearEntityNotFoundError


class DatabaseInfo(BaseSchema):
    name: str
    database: str
    description: str | None = None
    active: bool = True


class TenantConfig(BaseSchema):
    name: str
    ref: str

    # tenant variables
    prefix: str = ''
    databases: list[DatabaseInfo] = []


class TenantRegistry(BaseSchema):
    """Registry of tenant configurations"""
    tenants: dict[str, TenantConfig] = pydantic.Field(default_factory=dict)

    @classmethod
    def load(cls, filename: str):
        """Load tenant configurations from a YAML file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def save(self, filename: str) -> None:
        """Save tenant configurations to a YAML file"""
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True
                ),
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False)

    def __getitem__(self, name: str) -> TenantConfig:
        return self.tenants[name]

    def __iter__(self):
        yield from self.tenants.values()

    def __len__(self) -> int:
        return len(self.tenants)

    def __contains__(self, name: str) -> bool:
        return name in self.tenants

    def add(self, tenant: TenantConfig) -> None:
        if tenant.name in self.tenants:
            raise DBGearEntityExistsError(f'Tenant {tenant.name} already exists')
        self.tenants[tenant.name] = tenant

    def remove(self, name: str) -> None:
        if name not in self.tenants:
            raise DBGearEntityNotFoundError(f'Tenant {name} does not exist')
        del self.tenants[name]
