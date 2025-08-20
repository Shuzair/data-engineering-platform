"""Check platform status."""

import click
import subprocess
from platform.core.logger import logger
from platform.core.state_manager import StateManager
from rich.table import Table
from rich.console import Console

@click.command()
@click.pass_context
def status(ctx):
    """Check platform status."""
    console = Console()
    
    # Check platform state
    state_manager = StateManager()
    platform_status = state_manager.get_platform_status()
    
    logger.info(f"Platform status: {platform_status}")
    
    # Check Docker containers
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout:
            import json
            containers = json.loads(result.stdout)
            
            # Create table
            table = Table(title="Service Status")
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Ports")
            
            for container in containers:
                status_color = "green" if "Up" in container.get("State", "") else "red"
                table.add_row(
                    container.get("Service", ""),
                    f"[{status_color}]{container.get('State', '')}[/{status_color}]",
                    container.get("Ports", "")
                )
            
            console.print(table)
    except Exception as e:
        logger.warning(f"Could not get container status: {e}")
