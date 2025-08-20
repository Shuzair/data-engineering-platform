"""View service logs."""

import click
import subprocess
from platform.core.logger import logger

@click.command()
@click.argument('service', required=False)
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--tail', '-n', default=100, help='Number of lines to show')
@click.pass_context
def logs(ctx, service, follow, tail):
    """View service logs."""
    cmd = ["docker-compose", "logs", f"--tail={tail}"]
    
    if follow:
        cmd.append("-f")
    
    if service:
        cmd.append(service)
    
    try:
        subprocess.run(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get logs: {e}")
    except KeyboardInterrupt:
        pass  # User stopped following logs
