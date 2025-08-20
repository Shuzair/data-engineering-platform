"""Base service class for all platform services."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

class BaseService(ABC):
    """Abstract base class for all services."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", False)
        self.version = config.get("version", "latest")
        self.image = None
        self.container_name = f"platform_{name}"
        self.ports = []
        self.volumes = []
        self.networks = ["platform_network"]
        self.environment = {}
        self.depends_on = []
        self.healthcheck = None
        self.labels = {
            "platform": "data-engineering",
            "service": name,
            "version": "2.0.0"
        }
        
        # Resource limits
        self.memory = config.get("memory", "1G")
        self.cpu = config.get("cpu", 1.0)
        
        # Service capabilities
        self.provides = []  # What this service provides
        self.requires = []  # What this service needs
        
        # Startup configuration
        self.startup_priority = 100
        self.startup_timeout = 60
        self.readiness_probe = None
    
    @abstractmethod
    def configure(self):
        """Configure the service with specific settings."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate service configuration."""
        pass
    
    def get_compose_config(self) -> Dict[str, Any]:
        """Generate docker-compose configuration for this service."""
        config = {
            "image": self.image,
            "container_name": self.container_name,
            "restart": "unless-stopped",
            "networks": self.networks,
            "labels": self.labels,
            "deploy": {
                "resources": {
                    "limits": {
                        "memory": self.memory,
                        "cpus": str(self.cpu)
                    }
                }
            }
        }
        
        # Add optional configurations
        if self.ports:
            config["ports"] = self.ports
        
        if self.volumes:
            config["volumes"] = self.volumes
        
        if self.environment:
            config["environment"] = self.environment
        
        if self.depends_on:
            config["depends_on"] = self.depends_on
        
        if self.healthcheck:
            config["healthcheck"] = self.healthcheck
        
        return config
    
    def pre_start_setup(self) -> bool:
        """Run any setup required before starting the service."""
        return True
    
    def post_start_setup(self) -> bool:
        """Run any setup required after starting the service."""
        return True
    
    def check_health(self) -> bool:
        """Check if the service is healthy."""
        return True
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for this service."""
        return {
            "host": self.container_name,
            "internal_host": self.container_name,
            "external_host": "localhost"
        }
    
    def get_dependencies(self) -> List[str]:
        """Get list of service dependencies."""
        return self.depends_on
    
    def set_dependency(self, service_name: str):
        """Add a dependency to this service."""
        if service_name not in self.depends_on:
            self.depends_on.append(service_name)
