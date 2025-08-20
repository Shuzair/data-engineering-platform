"""Docker operations manager."""

import docker
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from docker.errors import DockerException, APIError
from .logger import logger

class DockerManager:
    """Manages Docker operations for the platform."""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.api_client = docker.APIClient()
            logger.debug("Docker client initialized")
        except DockerException as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise
    
    def check_docker_running(self) -> bool:
        """Check if Docker daemon is running."""
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get_docker_info(self) -> Dict[str, Any]:
        """Get Docker system information."""
        try:
            info = self.client.info()
            return {
                "version": info.get("ServerVersion"),
                "os": info.get("OperatingSystem"),
                "total_memory": info.get("MemTotal", 0) / (1024**3),  # Convert to GB
                "cpus": info.get("NCPU", 0),
                "driver": info.get("Driver"),
                "docker_root": info.get("DockerRootDir"),
                "containers": {
                    "total": info.get("Containers", 0),
                    "running": info.get("ContainersRunning", 0),
                    "stopped": info.get("ContainersStopped", 0)
                }
            }
        except Exception as e:
            logger.error(f"Failed to get Docker info: {e}")
            return {}
    
    def create_network(self, name: str, subnet: str = "172.28.0.0/16") -> bool:
        """Create Docker network."""
        try:
            # Check if network exists
            existing_networks = self.client.networks.list(names=[name])
            if existing_networks:
                logger.info(f"Network '{name}' already exists")
                return True
            
            # Create network
            ipam_config = docker.types.IPAMConfig(
                pool_configs=[
                    docker.types.IPAMPool(subnet=subnet)
                ]
            )
            
            network = self.client.networks.create(
                name=name,
                driver="bridge",
                ipam=ipam_config,
                check_duplicate=True
            )
            
            logger.success(f"Created network '{name}' with subnet {subnet}")
            return True
            
        except APIError as e:
            logger.error(f"Failed to create network: {e}")
            return False
    
    def create_volume(self, name: str, driver: str = "local", 
                     driver_opts: Optional[Dict] = None) -> bool:
        """Create Docker volume."""
        try:
            # Check if volume exists
            try:
                volume = self.client.volumes.get(name)
                logger.info(f"Volume '{name}' already exists")
                return True
            except docker.errors.NotFound:
                pass
            
            # Create volume
            volume = self.client.volumes.create(
                name=name,
                driver=driver,
                driver_opts=driver_opts or {}
            )
            
            logger.success(f"Created volume '{name}'")
            return True
            
        except APIError as e:
            logger.error(f"Failed to create volume: {e}")
            return False
    
    def generate_compose_file(self, config: Dict[str, Any], output_path: Path):
        """Generate docker-compose.yaml from configuration."""
        compose = {
            "version": "3.8",
            "services": {},
            "networks": {
                "platform_network": {
                    "driver": "bridge",
                    "ipam": {
                        "config": [{"subnet": "172.28.0.0/16"}]
                    }
                }
            },
            "volumes": {}
        }
        
        # Add services
        for service_name, service_config in config.get("services", {}).items():
            if service_config.get("enabled", False):
                compose["services"][service_name] = self._generate_service_config(
                    service_name, service_config
                )
                
                # Add volumes for the service
                compose["volumes"][f"{service_name}_data"] = {
                    "driver": "local"
                }
        
        # Write compose file
        with open(output_path, 'w') as f:
            yaml.dump(compose, f, default_flow_style=False, sort_keys=False)
        
        logger.success(f"Generated docker-compose.yaml at {output_path}")
    
    def _generate_service_config(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service configuration for docker-compose."""
        service = {
            "container_name": f"platform_{name}",
            "restart": "unless-stopped",
            "networks": ["platform_network"],
            "volumes": [f"{name}_data:/data"],
            "environment": {},
            "deploy": {
                "resources": {
                    "limits": {
                        "memory": config.get("memory", "1G"),
                        "cpus": str(config.get("cpu", 1.0))
                    }
                }
            }
        }
        
        # Service-specific configurations
        if name == "postgresql":
            service.update({
                "image": f"postgres:{config.get('version', '16-alpine')}",
                "ports": [f"{config.get('port', 5432)}:5432"],
                "environment": {
                    "POSTGRES_DB": "datawarehouse",
                    "POSTGRES_USER": "postgres",
                    "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}"
                },
                "volumes": [
                    "postgres_data:/var/lib/postgresql/data"
                ],
                "healthcheck": {
                    "test": ["CMD-SHELL", "pg_isready -U postgres"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            })
        
        # Add more service-specific configurations here
        
        return service
    
    def pull_images(self, services: List[str], config: Dict[str, Any]):
        """Pull Docker images for services."""
        for service_name in services:
            service_config = config.get("services", {}).get(service_name, {})
            if not service_config.get("enabled", False):
                continue
            
            # Determine image name
            image_name = self._get_image_name(service_name, service_config)
            
            try:
                logger.info(f"Pulling image: {image_name}")
                image = self.client.images.pull(image_name)
                logger.success(f"Pulled image: {image_name}")
            except Exception as e:
                logger.error(f"Failed to pull {image_name}: {e}")
    
    def _get_image_name(self, service_name: str, config: Dict[str, Any]) -> str:
        """Get Docker image name for a service."""
        image_map = {
            "postgresql": f"postgres:{config.get('version', '16-alpine')}",
            "airflow": f"apache/airflow:{config.get('version', '2.9.3')}",
            "spark": f"bitnami/spark:{config.get('version', '3.5.1')}",
            "jupyter": f"jupyter/pyspark-notebook:{config.get('version', 'spark-3.5.1')}",
            "pgadmin": f"dpage/pgadmin4:{config.get('version', '8.11')}"
        }
        return image_map.get(service_name, f"{service_name}:latest")
    
    def check_port_availability(self, port: int) -> bool:
        """Check if a port is available."""
        import socket
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return True
            except:
                return False
    
    def get_container_status(self, container_name: str) -> Optional[str]:
        """Get container status."""
        try:
            container = self.client.containers.get(container_name)
            return container.status
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return None
    
    def execute_in_container(self, container_name: str, command: str) -> Optional[str]:
        """Execute command in container."""
        try:
            container = self.client.containers.get(container_name)
            result = container.exec_run(command)
            return result.output.decode('utf-8') if result.output else None
        except Exception as e:
            logger.error(f"Failed to execute command in {container_name}: {e}")
            return None
