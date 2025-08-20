"""CLI entry point."""
import click
from platform.core.logger import logger

@click.group()
@click.version_option(version="2.0.0")
def cli():
    """Data Engineering Platform CLI."""
    pass

@cli.command()
def init():
    """Initialize the platform."""
    logger.print_banner()
    logger.info("Platform initialization started...")
    # TODO: Add initialization logic

def main():
    """Main entry point."""
    cli()

if __name__ == "__main__":
    main()
