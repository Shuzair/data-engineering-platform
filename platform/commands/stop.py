"""Stop platform services."""

import click
import subprocess
from platform.core.logger import logger

@click.command()
@click.argument('services', nargs=-1)
@click.pass_context
def stop(ctx, services):
    """Stop platform services."""
    logger.info("Stopping platform services...")
    
    cmd = ["docker-compose", "down"]
    if services:
        cmd = ["docker-compose", "stop"] + list(services)
    
    try:
        subprocess.run(cmd, check=True)
        logger.success("Services stopped")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stop services: {e}")
