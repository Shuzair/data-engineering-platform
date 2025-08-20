"""Configuration management system."""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
from .logger import logger

class ConfigManager:
    """Manages platform configuration."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd() / "config"
        self.platform_dir = Path.home() / ".platform"
        self.platform_dir.mkdir(exist_ok=True)
        
        # Configuration schema
        self.schema = {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "environment": {
                            "type": "string",
                            "enum": ["development", "production", "custom"]
                        }
                    },
                    "required": ["name", "version", "environment"]
                },
                "resources": {
                    "type": "object",
                    "properties": {
                        "memory_limit": {"type": "string", "pattern": "^[0-9]+[GMK]$"},
                        "cpu_limit": {"type": "number"}
                    }
                },
                "services": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean"},
                            "version": {"type": "string"},
                            "memory": {"type": "string", "pattern": "^[0-9]+[GMK]$"},
                            "cpu": {"type": "number"}
                        }
                    }
                }
            },
            "required": ["platform"]
        }
    
    def load_config(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate against schema
            validate(instance=config, schema=self.schema)
            logger.success(f"Configuration loaded from {config_file}")
            return config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_file}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e.message}")
            raise
    
    def save_config(self, config: Dict[str, Any], config_file: Path):
        """Save configuration to YAML file."""
        try:
            # Validate before saving
            validate(instance=config, schema=self.schema)
            
            # Create directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            logger.success(f"Configuration saved to {config_file}")
            
        except ValidationError as e:
            logger.error(f"Invalid configuration: {e.message}")
            raise
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            "platform": {
                "name": "data-engineering-platform",
                "version": "2.0.0",
                "environment": "development"
            },
            "resources": {
                "memory_limit": "8G",
                "cpu_limit": 4
            },
            "services": {
                "postgresql": {
                    "enabled": True,
                    "version": "16-alpine",
                    "memory": "2G",
                    "cpu": 1.0,
                    "port": 5432
                },
                "airflow": {
                    "enabled": True,
                    "version": "2.9.3",
                    "memory": "2G",
                    "cpu": 1.0,
                    "port": 8080
                },
                "spark": {
                    "enabled": True,
                    "version": "3.5.1",
                    "memory": "4G",
                    "cpu": 2.0,
                    "master_port": 7077,
                    "ui_port": 8082
                },
                "jupyter": {
                    "enabled": True,
                    "version": "spark-3.5.1",
                    "memory": "2G",
                    "cpu": 1.0,
                    "port": 8888
                },
                "dbt": {
                    "enabled": True,
                    "version": "1.8.0",
                    "memory": "1G",
                    "cpu": 0.5
                },
                "pgadmin": {
                    "enabled": True,
                    "version": "8.11",
                    "memory": "512M",
                    "cpu": 0.5,
                    "port": 8081
                }
            }
        }
    
    def merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configurations, with override taking precedence."""
        def deep_merge(dict1, dict2):
            result = dict1.copy()
            for key, value in dict2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(base, override)
