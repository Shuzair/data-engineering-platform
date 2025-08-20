"""Main Platform class."""
from .config import ConfigManager
from .docker_manager import DockerManager
from .state_manager import StateManager
from .logger import logger

class Platform:
    """Main platform orchestrator."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.docker = DockerManager()
        self.state = StateManager()
        logger.debug("Platform initialized")
