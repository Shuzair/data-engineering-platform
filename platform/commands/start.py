"""Start platform services."""

import click
import subprocess
from platform.core.logger import logger

@click.command()
@click.argument('services', nargs=-1)
@click.option('--detach', '-d', is_flag=True, help='Run in background')
@click.pass_context
def start(ctx, services, detach):
    """Start platform services."""
    logger.info("Starting platform services...")
    
    cmd = ["docker-compose", "up"]
    if detach:
        cmd.append("-d")
    if services:
        cmd.extend(services)
    
    try:
        result = subprocess.run(cmd, check=True)
        if detach:
            logger.success("Services started in background")
            logger.info("Check status: platform status")
        else:
            logger.info("Services running in foreground (Ctrl+C to stop)")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start services: {e}")
    except FileNotFoundError:
        logger.error("docker-compose not found. Is Docker installed?")
