"""
Patch processing module for DBGear.

Handles YAML patch file parsing and SQL generation for custom data restoration.
"""

import yaml
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PatchConfig:
    """Represents a patch configuration loaded from YAML."""
    
    def __init__(self, name: str, select: List[str], where: Optional[str] = None):
        self.name = name
        self.select = select
        self.where = where
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PatchConfig':
        """Create PatchConfig from dictionary."""
        if 'name' not in data:
            raise ValueError("Patch config must have 'name' field")
        if 'select' not in data:
            raise ValueError("Patch config must have 'select' field")
        
        return cls(
            name=data['name'],
            select=data['select'],
            where=data.get('where')
        )
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'PatchConfig':
        """Load patch configuration from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return cls.from_dict(data)
        except FileNotFoundError:
            raise ValueError(f"Patch file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in patch file: {e}")


def generate_patch_sql(env: str, patch_config: PatchConfig, backup_key: str) -> str:
    """
    Generate INSERT SQL from patch configuration.
    
    Args:
        env: Database environment name
        patch_config: Patch configuration
        backup_key: Backup table timestamp key (YYYYMMDDHHMMSS)
    
    Returns:
        Generated INSERT SQL string
    """
    table_name = patch_config.name
    backup_table = f"bak_{table_name}_{backup_key}"
    
    # Build SELECT columns
    select_columns = ",\n  ".join(patch_config.select)
    
    # Build WHERE clause if specified
    where_clause = ""
    if patch_config.where:
        where_clause = f"\nWHERE {patch_config.where}"
    
    # Generate final SQL
    sql = f"""INSERT INTO {env}.{table_name}
SELECT
  {select_columns}
FROM {env}.{backup_table}{where_clause}"""
    
    return sql


def validate_patch_config(patch_config: PatchConfig) -> List[str]:
    """
    Validate patch configuration and return list of warnings/errors.
    
    Returns:
        List of validation messages (empty if valid)
    """
    errors = []
    
    if not patch_config.name:
        errors.append("Table name cannot be empty")
    
    if not patch_config.select:
        errors.append("Select columns cannot be empty")
    
    # Check for common SQL injection patterns in WHERE clause
    if patch_config.where:
        dangerous_patterns = [';', '--', '/*', '*/', 'DROP', 'DELETE', 'UPDATE']
        where_upper = patch_config.where.upper()
        for pattern in dangerous_patterns:
            if pattern in where_upper:
                errors.append(f"Potentially dangerous pattern '{pattern}' found in WHERE clause")
                break
    
    return errors