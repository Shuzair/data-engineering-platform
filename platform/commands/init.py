"""Initialize platform command."""

import click
import sys
from pathlib import Path
from typing import Dict, Any
from platform.core.logger import logger
from platform.core.config import ConfigManager
from platform.core.docker_manager import DockerManager
from platform.core.state_manager import StateManager
from platform.services.postgresql import PostgreSQLService

@click.command()
@click.option('--config', type=click.Path(), help='Configuration file path')
@click.option('--wizard', is_flag=True, help='Run interactive setup wizard')
@click.option('--force', is_flag=True, help='Force initialization')
@click.pass_context
def init(ctx, config, wizard, force):
    """Initialize the data engineering platform."""
    logger.print_banner()
    
    # Check if already initialized
    state_manager = StateManager()
    if state_manager.get_platform_status() == "initialized" and not force:
        logger.warning("Platform is already initialized")
        if not click.confirm("Do you want to reinitialize?"):
            return
    
    # Check Docker
    docker = DockerManager()
    if not docker.check_docker_running():
        logger.error("Docker is not running. Please start Docker first.")
        sys.exit(1)
    
    # Show Docker info
    docker_info = docker.get_docker_info()
    logger.info(f"Docker version: {docker_info.get('version')}")
    logger.info(f"Available memory: {docker_info.get('total_memory'):.1f}GB")
    logger.info(f"Available CPUs: {docker_info.get('cpus')}")
    
    # Load or create configuration
    config_manager = ConfigManager()
    
    if wizard:
        platform_config = run_wizard(config_manager)
    elif config:
        platform_config = config_manager.load_config(Path(config))
    else:
        platform_config = config_manager.create_default_config()
    
    # Save configuration
    config_file = Path("config") / "platform.yaml"
    config_manager.save_config(platform_config, config_file)
    
    # Initialize services
    logger.info("Initializing services...")
    
    # Create PostgreSQL service
    if platform_config["services"]["postgresql"]["enabled"]:
        pg_service = PostgreSQLService(platform_config["services"]["postgresql"])
        if pg_service.validate_config():
            pg_service.pre_start_setup()
            logger.success(f"PostgreSQL service configured")
            
            # Save connection info
            conn_info = pg_service.get_connection_info()
            save_env_file({"POSTGRES_PASSWORD": conn_info["password"]})
    
    # Create network
    docker.create_network("platform_network")
    
    # Create volumes
    for service_name, service_config in platform_config["services"].items():
        if service_config.get("enabled"):
            docker.create_volume(f"{service_name}_data")
    
    # Generate docker-compose.yaml
    docker.generate_compose_file(platform_config, Path("docker-compose.yaml"))
    
    # Update state
    state_manager.set_platform_status("initialized")
    
    logger.success("Platform initialized successfully!")
    logger.info("Next steps:")
    logger.info("  1. Review configuration in config/platform.yaml")
    logger.info("  2. Start services: platform start")
    logger.info("  3. Check status: platform status")

def run_wizard(config_manager: ConfigManager) -> Dict[str, Any]:
    """Run interactive setup wizard."""
    logger.info("Starting interactive setup wizard...")
    
    config = config_manager.create_default_config()
    
    # Platform settings
    config["platform"]["name"] = click.prompt("Platform name", 
                                             default=config["platform"]["name"])
    
    config["platform"]["environment"] = click.prompt(
        "Environment",
        type=click.Choice(["development", "production"]),
        default="development"
    )
    
    # Resource settings
    config["resources"]["memory_limit"] = click.prompt(
        "Memory limit (e.g., 8G)",
        default=config["resources"]["memory_limit"]
    )
    
    config["resources"]["cpu_limit"] = click.prompt(
        "CPU limit",
        type=int,
        default=config["resources"]["cpu_limit"]
    )
    
    # Service selection
    logger.info("\nSelect services to enable:")
    
    for service_name in config["services"]:
        config["services"][service_name]["enabled"] = click.confirm(
            f"  Enable {service_name}?",
            default=config["services"][service_name]["enabled"]
        )
    
    return config

def save_env_file(env_vars: Dict[str, str]):
    """Save environment variables to .env file."""
    env_file = Path(".env")
    
    lines = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update or add variables
    for key, value in env_vars.items():
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                found = True
                break
        if not found:
            lines.append(f"{key}={value}\n")
    
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    logger.debug(f"Updated .env file")
