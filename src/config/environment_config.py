"""
Environment Configuration

This module handles environment-specific configurations for different
deployment scenarios (development, staging, production).
"""

import os
import json
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from ..utils.logger import get_logger


class Environment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    decode_responses: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str
    jwt_secret: str
    jwt_expiration_hours: int = 24
    password_salt_rounds: int = 12
    rate_limit_per_minute: int = 60
    cors_origins: List[str] = None
    csrf_protection: bool = True
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    enabled: bool = True
    metrics_endpoint: str = "/metrics"
    health_endpoint: str = "/health"
    sentry_dsn: Optional[str] = None
    datadog_api_key: Optional[str] = None
    prometheus_enabled: bool = False


@dataclass
class PerformanceConfig:
    """Performance and scaling configuration."""
    worker_processes: int = 1
    worker_threads: int = 4
    max_requests_per_worker: int = 1000
    request_timeout: int = 30
    keep_alive_timeout: int = 2
    max_concurrent_requests: int = 100


class EnvironmentConfigManager:
    """
    Environment-specific configuration manager.
    
    Handles loading and managing configurations for different
    deployment environments with appropriate defaults and overrides.
    """
    
    def __init__(self, environment: Optional[Environment] = None):
        """
        Initialize the environment configuration manager.
        
        Args:
            environment: Target environment (auto-detected if None)
        """
        self.logger = get_logger("environment_config")
        
        # Determine environment
        self.environment = environment or self._detect_environment()
        
        # Configuration storage
        self.database_config: Optional[DatabaseConfig] = None
        self.redis_config: Optional[RedisConfig] = None
        self.logging_config: LoggingConfig = LoggingConfig()
        self.security_config: Optional[SecurityConfig] = None
        self.monitoring_config: MonitoringConfig = MonitoringConfig()
        self.performance_config: PerformanceConfig = PerformanceConfig()
        
        # Load environment-specific configurations
        self._load_environment_config()
        
        self.logger.info(f"Environment configuration loaded for: {self.environment.value}")
    
    def _detect_environment(self) -> Environment:
        """Auto-detect the current environment."""
        # Check environment variable
        env_name = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
        
        # Map common variations
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "local": Environment.DEVELOPMENT,
            "stage": Environment.STAGING,
            "staging": Environment.STAGING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "test": Environment.TESTING,
            "testing": Environment.TESTING
        }
        
        return env_mapping.get(env_name, Environment.DEVELOPMENT)
    
    def _load_environment_config(self):
        """Load environment-specific configurations."""
        # Load database configuration
        self._load_database_config()
        
        # Load Redis configuration
        self._load_redis_config()
        
        # Load logging configuration
        self._load_logging_config()
        
        # Load security configuration
        self._load_security_config()
        
        # Load monitoring configuration
        self._load_monitoring_config()
        
        # Load performance configuration
        self._load_performance_config()
    
    def _load_database_config(self):
        """Load database configuration."""
        # Get database URL from environment
        db_url = os.getenv("DATABASE_URL")
        
        if db_url:
            # Environment-specific database settings
            if self.environment == Environment.PRODUCTION:
                self.database_config = DatabaseConfig(
                    url=db_url,
                    pool_size=20,
                    max_overflow=30,
                    pool_timeout=60,
                    pool_recycle=3600,
                    echo=False
                )
            elif self.environment == Environment.STAGING:
                self.database_config = DatabaseConfig(
                    url=db_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    pool_recycle=3600,
                    echo=False
                )
            elif self.environment == Environment.DEVELOPMENT:
                self.database_config = DatabaseConfig(
                    url=db_url,
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800,
                    echo=True
                )
            elif self.environment == Environment.TESTING:
                self.database_config = DatabaseConfig(
                    url=db_url,
                    pool_size=1,
                    max_overflow=5,
                    pool_timeout=10,
                    pool_recycle=300,
                    echo=False
                )
        else:
            # Default SQLite for development/testing
            if self.environment in [Environment.DEVELOPMENT, Environment.TESTING]:
                db_path = "social_media_agent.db"
                if self.environment == Environment.TESTING:
                    db_path = "test_social_media_agent.db"
                
                self.database_config = DatabaseConfig(
                    url=f"sqlite:///{db_path}",
                    pool_size=1,
                    max_overflow=0,
                    echo=self.environment == Environment.DEVELOPMENT
                )
    
    def _load_redis_config(self):
        """Load Redis configuration."""
        redis_url = os.getenv("REDIS_URL")
        
        if redis_url:
            # Environment-specific Redis settings
            if self.environment == Environment.PRODUCTION:
                self.redis_config = RedisConfig(
                    url=redis_url,
                    max_connections=20,
                    socket_timeout=10,
                    socket_connect_timeout=10,
                    retry_on_timeout=True
                )
            elif self.environment == Environment.STAGING:
                self.redis_config = RedisConfig(
                    url=redis_url,
                    max_connections=10,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
            else:
                self.redis_config = RedisConfig(
                    url=redis_url,
                    max_connections=5,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=False
                )
        else:
            # Default Redis configuration for development
            if self.environment in [Environment.DEVELOPMENT, Environment.TESTING]:
                self.redis_config = RedisConfig(
                    url="redis://localhost:6379/0",
                    max_connections=5,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=False
                )
    
    def _load_logging_config(self):
        """Load logging configuration."""
        # Environment-specific logging settings
        if self.environment == Environment.PRODUCTION:
            self.logging_config = LoggingConfig(
                level=os.getenv("LOG_LEVEL", "WARNING"),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d",
                file_path="/var/log/social-media-agent/app.log",
                max_file_size=52428800,  # 50MB
                backup_count=10,
                console_output=False
            )
        elif self.environment == Environment.STAGING:
            self.logging_config = LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d",
                file_path="logs/staging.log",
                max_file_size=20971520,  # 20MB
                backup_count=5,
                console_output=True
            )
        elif self.environment == Environment.DEVELOPMENT:
            self.logging_config = LoggingConfig(
                level=os.getenv("LOG_LEVEL", "DEBUG"),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                file_path="logs/development.log",
                max_file_size=10485760,  # 10MB
                backup_count=3,
                console_output=True
            )
        elif self.environment == Environment.TESTING:
            self.logging_config = LoggingConfig(
                level=os.getenv("LOG_LEVEL", "ERROR"),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                file_path=None,  # No file logging for tests
                console_output=False
            )
    
    def _load_security_config(self):
        """Load security configuration."""
        # Generate or load secret keys
        secret_key = os.getenv("SECRET_KEY")
        jwt_secret = os.getenv("JWT_SECRET")
        
        if not secret_key:
            if self.environment == Environment.PRODUCTION:
                raise ValueError("SECRET_KEY must be set in production environment")
            else:
                secret_key = "dev-secret-key-not-for-production"
        
        if not jwt_secret:
            if self.environment == Environment.PRODUCTION:
                raise ValueError("JWT_SECRET must be set in production environment")
            else:
                jwt_secret = "dev-jwt-secret-not-for-production"
        
        # Environment-specific security settings
        if self.environment == Environment.PRODUCTION:
            cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
            self.security_config = SecurityConfig(
                secret_key=secret_key,
                jwt_secret=jwt_secret,
                jwt_expiration_hours=24,
                password_salt_rounds=12,
                rate_limit_per_minute=100,
                cors_origins=cors_origins,
                csrf_protection=True
            )
        elif self.environment == Environment.STAGING:
            self.security_config = SecurityConfig(
                secret_key=secret_key,
                jwt_secret=jwt_secret,
                jwt_expiration_hours=12,
                password_salt_rounds=10,
                rate_limit_per_minute=200,
                cors_origins=["*"],
                csrf_protection=True
            )
        else:  # Development/Testing
            self.security_config = SecurityConfig(
                secret_key=secret_key,
                jwt_secret=jwt_secret,
                jwt_expiration_hours=168,  # 1 week for development
                password_salt_rounds=4,  # Faster for development
                rate_limit_per_minute=1000,
                cors_origins=["*"],
                csrf_protection=False
            )
    
    def _load_monitoring_config(self):
        """Load monitoring configuration."""
        # Environment-specific monitoring settings
        if self.environment == Environment.PRODUCTION:
            self.monitoring_config = MonitoringConfig(
                enabled=True,
                metrics_endpoint="/metrics",
                health_endpoint="/health",
                sentry_dsn=os.getenv("SENTRY_DSN"),
                datadog_api_key=os.getenv("DATADOG_API_KEY"),
                prometheus_enabled=True
            )
        elif self.environment == Environment.STAGING:
            self.monitoring_config = MonitoringConfig(
                enabled=True,
                metrics_endpoint="/metrics",
                health_endpoint="/health",
                sentry_dsn=os.getenv("SENTRY_DSN"),
                datadog_api_key=os.getenv("DATADOG_API_KEY"),
                prometheus_enabled=True
            )
        else:  # Development/Testing
            self.monitoring_config = MonitoringConfig(
                enabled=self.environment == Environment.DEVELOPMENT,
                metrics_endpoint="/metrics",
                health_endpoint="/health",
                sentry_dsn=None,
                datadog_api_key=None,
                prometheus_enabled=False
            )
    
    def _load_performance_config(self):
        """Load performance configuration."""
        # Environment-specific performance settings
        if self.environment == Environment.PRODUCTION:
            self.performance_config = PerformanceConfig(
                worker_processes=int(os.getenv("WORKER_PROCESSES", "4")),
                worker_threads=int(os.getenv("WORKER_THREADS", "8")),
                max_requests_per_worker=1000,
                request_timeout=30,
                keep_alive_timeout=5,
                max_concurrent_requests=500
            )
        elif self.environment == Environment.STAGING:
            self.performance_config = PerformanceConfig(
                worker_processes=int(os.getenv("WORKER_PROCESSES", "2")),
                worker_threads=int(os.getenv("WORKER_THREADS", "4")),
                max_requests_per_worker=500,
                request_timeout=30,
                keep_alive_timeout=2,
                max_concurrent_requests=200
            )
        else:  # Development/Testing
            self.performance_config = PerformanceConfig(
                worker_processes=1,
                worker_threads=2,
                max_requests_per_worker=100,
                request_timeout=60,  # Longer for debugging
                keep_alive_timeout=2,
                max_concurrent_requests=50
            )
    
    # Public API methods
    
    def get_environment(self) -> Environment:
        """Get current environment."""
        return self.environment
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.environment == Environment.TESTING
    
    def get_database_config(self) -> Optional[DatabaseConfig]:
        """Get database configuration."""
        return self.database_config
    
    def get_redis_config(self) -> Optional[RedisConfig]:
        """Get Redis configuration."""
        return self.redis_config
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self.logging_config
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.security_config
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return self.monitoring_config
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration."""
        return self.performance_config
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for the current configuration."""
        env_vars = {
            "ENVIRONMENT": self.environment.value,
            "LOG_LEVEL": self.logging_config.level,
        }
        
        # Add database URL if configured
        if self.database_config:
            env_vars["DATABASE_URL"] = self.database_config.url
        
        # Add Redis URL if configured
        if self.redis_config:
            env_vars["REDIS_URL"] = self.redis_config.url
        
        # Add security variables (without exposing secrets)
        if self.security_config:
            env_vars["JWT_EXPIRATION_HOURS"] = str(self.security_config.jwt_expiration_hours)
            env_vars["RATE_LIMIT_PER_MINUTE"] = str(self.security_config.rate_limit_per_minute)
        
        # Add monitoring variables
        if self.monitoring_config.sentry_dsn:
            env_vars["SENTRY_DSN"] = self.monitoring_config.sentry_dsn
        
        return env_vars
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the current configuration.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate production requirements
        if self.environment == Environment.PRODUCTION:
            if not self.database_config:
                errors.append("Database configuration required for production")
            
            if not self.security_config:
                errors.append("Security configuration required for production")
            elif (self.security_config.secret_key == "dev-secret-key-not-for-production" or
                  self.security_config.jwt_secret == "dev-jwt-secret-not-for-production"):
                errors.append("Production secret keys must be set via environment variables")
            
            if not self.redis_config:
                errors.append("Redis configuration recommended for production")
        
        # Validate database configuration
        if self.database_config:
            if not self.database_config.url:
                errors.append("Database URL is required")
            
            if self.database_config.pool_size <= 0:
                errors.append("Database pool size must be positive")
        
        # Validate Redis configuration
        if self.redis_config:
            if not self.redis_config.url:
                errors.append("Redis URL is required")
        
        # Validate logging configuration
        if self.logging_config.file_path:
            log_dir = Path(self.logging_config.file_path).parent
            if not log_dir.exists():
                try:
                    log_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    errors.append(f"Cannot create log directory: {log_dir}")
        
        return errors
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration (without secrets)."""
        config_export = {
            "environment": self.environment.value,
            "database": asdict(self.database_config) if self.database_config else None,
            "redis": asdict(self.redis_config) if self.redis_config else None,
            "logging": asdict(self.logging_config),
            "monitoring": asdict(self.monitoring_config),
            "performance": asdict(self.performance_config)
        }
        
        # Export security config without secrets
        if self.security_config:
            security_export = asdict(self.security_config)
            security_export["secret_key"] = "[REDACTED]"
            security_export["jwt_secret"] = "[REDACTED]"
            config_export["security"] = security_export
        
        return config_export
    
    def setup_logging(self):
        """Setup logging based on current configuration."""
        import logging
        import logging.handlers
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.logging_config.level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(self.logging_config.format)
        
        # Console handler
        if self.logging_config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.logging_config.file_path:
            # Ensure log directory exists
            log_dir = Path(self.logging_config.file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.logging_config.file_path,
                maxBytes=self.logging_config.max_file_size,
                backupCount=self.logging_config.backup_count
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        self.logger.info(f"Logging configured for {self.environment.value} environment")
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask-specific configuration."""
        flask_config = {}
        
        if self.security_config:
            flask_config.update({
                "SECRET_KEY": self.security_config.secret_key,
                "JWT_SECRET_KEY": self.security_config.jwt_secret,
                "JWT_ACCESS_TOKEN_EXPIRES": self.security_config.jwt_expiration_hours * 3600,
                "WTF_CSRF_ENABLED": self.security_config.csrf_protection,
            })
        
        if self.database_config:
            flask_config["SQLALCHEMY_DATABASE_URI"] = self.database_config.url
            flask_config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_size": self.database_config.pool_size,
                "max_overflow": self.database_config.max_overflow,
                "pool_timeout": self.database_config.pool_timeout,
                "pool_recycle": self.database_config.pool_recycle,
                "echo": self.database_config.echo
            }
        
        # Environment-specific Flask settings
        if self.environment == Environment.PRODUCTION:
            flask_config.update({
                "DEBUG": False,
                "TESTING": False,
                "PROPAGATE_EXCEPTIONS": False
            })
        elif self.environment == Environment.DEVELOPMENT:
            flask_config.update({
                "DEBUG": True,
                "TESTING": False,
                "PROPAGATE_EXCEPTIONS": True
            })
        elif self.environment == Environment.TESTING:
            flask_config.update({
                "DEBUG": False,
                "TESTING": True,
                "PROPAGATE_EXCEPTIONS": True
            })
        
        return flask_config
    
    def get_celery_config(self) -> Dict[str, Any]:
        """Get Celery-specific configuration."""
        celery_config = {}
        
        if self.redis_config:
            celery_config.update({
                "broker_url": self.redis_config.url,
                "result_backend": self.redis_config.url,
                "broker_connection_retry_on_startup": True,
                "broker_connection_retry": True,
                "result_expires": 3600,  # 1 hour
            })
        
        # Environment-specific Celery settings
        if self.environment == Environment.PRODUCTION:
            celery_config.update({
                "worker_prefetch_multiplier": 1,
                "task_acks_late": True,
                "worker_max_tasks_per_child": 1000,
            })
        elif self.environment == Environment.DEVELOPMENT:
            celery_config.update({
                "worker_prefetch_multiplier": 4,
                "task_acks_late": False,
                "task_always_eager": False,
            })
        elif self.environment == Environment.TESTING:
            celery_config.update({
                "task_always_eager": True,
                "task_eager_propagates": True,
            })
        
        return celery_config

