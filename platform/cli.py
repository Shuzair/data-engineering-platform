"""CLI entry point for the platform."""

import click
import sys
from pathlib import Path
from platform.core.logger import logger
from platform.commands import init, start, stop, status, logs

@click.group()
@click.version_option(version="2.0.0", prog_name="Data Engineering Platform")
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx, debug):
    """
    Data Engineering Platform CLI
    
    A modern, modular platform for data engineering.
    """
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    
    if debug:
        import logging
        logger.logger.setLevel(logging.DEBUG)

# Register commands
cli.add_command(init.init)
cli.add_command(start.start)
cli.add_command(stop.stop)
cli.add_command(status.status)
cli.add_command(logs.logs)

def main():
    """Main entry point."""
    try:
        cli()
    except Exception as e:
        logger.error(f"Command failed: {e}")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
