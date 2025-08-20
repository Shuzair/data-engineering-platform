"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Custom theme for platform
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "debug": "dim white",
})

console = Console(theme=custom_theme)

class Logger:
    """Platform logger with rich output."""
    
    def __init__(self, name="platform", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler with rich
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setLevel(level)
        
        # File handler
        log_dir = Path.home() / ".platform" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / "platform.log",
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(f"[info]{message}[/info]")
    
    def warning(self, message):
        self.logger.warning(f"[warning]{message}[/warning]")
    
    def error(self, message):
        self.logger.error(f"[error]{message}[/error]")
    
    def success(self, message):
        console.print(f"✅ {message}", style="success")
    
    def print_banner(self):
        """Print platform banner."""
        banner = """
╔════════════════════════════════════════════════════════════╗
║          🚀 Data Engineering Platform v2.0                 ║
║                  Modern • Modular • Simple                 ║
╚════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="cyan")

# Global logger instance
logger = Logger()
