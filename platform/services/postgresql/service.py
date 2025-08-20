"""PostgreSQL service implementation."""

import secrets
from typing import Dict, Any
from ..base import BaseService
from platform.core.logger import logger

class PostgreSQLService(BaseService):
    """PostgreSQL database service."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("postgresql", config)
        
        # Service capabilities
        self.provides = ["sql_database", "data_warehouse"]
        self.requires = []
        
        # Startup configuration
        self.startup_priority = 10  # Start early
        self.startup_timeout = 30
        
        # Database configuration
        self.db_name = config.get("database", "datawarehouse")
        self.db_user = config.get("user", "postgres")
        self.db_password = None  # Will be generated
        self.db_port = config.get("port", 5432)
        
        self.configure()
    
    def configure(self):
        """Configure PostgreSQL service."""
        self.image = f"postgres:{self.version}"
        
        # Generate secure password if not provided
        if not self.db_password:
            self.db_password = secrets.token_urlsafe(32)
        
        # Port mapping
        self.ports = [f"{self.db_port}:5432"]
        
        # Volumes
        self.volumes = [
            "postgres_data:/var/lib/postgresql/data",
            "./sql:/docker-entrypoint-initdb.d:ro"  # SQL init scripts
        ]
        
        # Environment variables
        self.environment = {
            "POSTGRES_DB": self.db_name,
            "POSTGRES_USER": self.db_user,
            "POSTGRES_PASSWORD": self.db_password,
            "POSTGRES_INITDB_ARGS": "--encoding=UTF8 --locale=en_US.utf8",
            # Performance settings
            "POSTGRES_MAX_CONNECTIONS": "200",
            "POSTGRES_SHARED_BUFFERS": "256MB",
            "POSTGRES_EFFECTIVE_CACHE_SIZE": "1GB",
            "POSTGRES_MAINTENANCE_WORK_MEM": "128MB",
            "POSTGRES_WORK_MEM": "4MB"
        }
        
        # Health check
        self.healthcheck = {
            "test": ["CMD-SHELL", "pg_isready -U postgres"],
            "interval": "10s",
            "timeout": "5s",
            "retries": 5,
            "start_period": "10s"
        }
        
        # Set resource limits based on environment
        if self.config.get("environment") == "production":
            self.memory = self.config.get("memory", "4G")
            self.cpu = self.config.get("cpu", 2.0)
        
        logger.debug(f"PostgreSQL configured with database: {self.db_name}")
    
    def validate_config(self) -> bool:
        """Validate PostgreSQL configuration."""
        if not self.db_name:
            logger.error("Database name is required")
            return False
        
        if not self.db_user:
            logger.error("Database user is required")
            return False
        
        if self.db_port < 1 or self.db_port > 65535:
            logger.error(f"Invalid port number: {self.db_port}")
            return False
        
        return True
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get PostgreSQL connection information."""
        return {
            **super().get_connection_info(),
            "port": self.db_port,
            "database": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "jdbc_url": f"jdbc:postgresql://localhost:{self.db_port}/{self.db_name}",
            "connection_string": f"postgresql://{self.db_user}:{self.db_password}@localhost:{self.db_port}/{self.db_name}"
        }
    
    def pre_start_setup(self) -> bool:
        """Create SQL initialization scripts."""
        from pathlib import Path
        
        sql_dir = Path("sql")
        sql_dir.mkdir(exist_ok=True)
        
        # Create initialization SQL
        init_sql = sql_dir / "01_init.sql"
        if not init_sql.exists():
            with open(init_sql, 'w') as f:
                f.write("""
-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS ml;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create read-only role
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE datawarehouse TO readonly;
GRANT USAGE ON SCHEMA raw, staging, marts, ml TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw, staging, marts, ml 
    GRANT SELECT ON TABLES TO readonly;

-- Create ETL role
CREATE ROLE etl_user;
GRANT CONNECT ON DATABASE datawarehouse TO etl_user;
GRANT ALL ON SCHEMA raw, staging TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw, staging 
    GRANT ALL ON TABLES TO etl_user;
""")
            logger.info("Created PostgreSQL initialization script")
        
        return True
