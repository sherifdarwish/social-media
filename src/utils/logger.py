"""
Logging Utility

This module provides structured logging functionality for the social media agent system.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import structlog
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "getMessage", "exc_info", 
                          "exc_text", "stack_info"]:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format the message
        formatted = f"{color}[{timestamp}] {record.levelname:8} {record.name:20} | {record.getMessage()}{reset}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: str = "10MB",
    backup_count: int = 5,
    json_format: bool = False,
    console_output: bool = True
) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        json_format: Whether to use JSON formatting
        console_output: Whether to output to console
    """
    # Convert level string to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        if json_format:
            console_formatter = JSONFormatter()
        else:
            console_formatter = ColoredFormatter()
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Parse max file size
        size_multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        size_str = max_file_size.upper()
        
        max_bytes = 10 * 1024 * 1024  # Default 10MB
        for suffix, multiplier in size_multipliers.items():
            if size_str.endswith(suffix):
                size_value = float(size_str[:-len(suffix)])
                max_bytes = int(size_value * multiplier)
                break
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        
        # Always use JSON format for file logging
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if json_format else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class AgentLogger:
    """Enhanced logger for agents with context tracking."""
    
    def __init__(self, agent_name: str, platform: str):
        """
        Initialize agent logger.
        
        Args:
            agent_name: Name of the agent
            platform: Platform the agent manages
        """
        self.agent_name = agent_name
        self.platform = platform
        self.logger = get_logger(f"agent.{platform}")
        self.context = {
            "agent_name": agent_name,
            "platform": platform
        }
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        """Log message with agent context."""
        extra_context = {**self.context, **kwargs}
        getattr(self.logger, level)(message, extra=extra_context)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context("debug", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_context("error", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context("critical", message, **kwargs)
    
    def log_content_generation(self, content_type: str, topic: str, success: bool, **kwargs):
        """Log content generation activity."""
        self._log_with_context(
            "info" if success else "error",
            f"Content generation {'successful' if success else 'failed'}",
            content_type=content_type,
            topic=topic,
            success=success,
            **kwargs
        )
    
    def log_post_activity(self, post_id: str, action: str, success: bool, **kwargs):
        """Log posting activity."""
        self._log_with_context(
            "info" if success else "error",
            f"Post {action} {'successful' if success else 'failed'}",
            post_id=post_id,
            action=action,
            success=success,
            **kwargs
        )
    
    def log_metrics_update(self, metrics: Dict[str, Any]):
        """Log metrics update."""
        self._log_with_context(
            "debug",
            "Metrics updated",
            metrics=metrics
        )
    
    def log_coordination_message(self, message_type: str, direction: str, **kwargs):
        """Log coordination message."""
        self._log_with_context(
            "debug",
            f"Coordination message {direction}",
            message_type=message_type,
            direction=direction,
            **kwargs
        )


class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self, name: str):
        """
        Initialize performance logger.
        
        Args:
            name: Name for the performance logger
        """
        self.name = name
        self.logger = get_logger(f"performance.{name}")
        self.start_time = None
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.start_time = datetime.utcnow()
        self.operation = operation
        self.logger.debug(f"Started {operation}")
    
    def end_timer(self, success: bool = True, **kwargs):
        """End timing and log the result."""
        if self.start_time is None:
            self.logger.warning("Timer ended without being started")
            return
        
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        self.logger.info(
            f"Operation {'completed' if success else 'failed'}",
            extra={
                "operation": self.operation,
                "duration_seconds": duration,
                "success": success,
                **kwargs
            }
        )
        
        self.start_time = None
    
    def log_api_call(self, provider: str, endpoint: str, duration: float, success: bool, **kwargs):
        """Log API call performance."""
        self.logger.info(
            f"API call to {provider}",
            extra={
                "provider": provider,
                "endpoint": endpoint,
                "duration_seconds": duration,
                "success": success,
                **kwargs
            }
        )


def configure_logging_from_config(config: Dict[str, Any]):
    """
    Configure logging from configuration dictionary.
    
    Args:
        config: Logging configuration
    """
    setup_logging(
        level=config.get("level", "INFO"),
        log_file=config.get("file"),
        max_file_size=config.get("max_file_size", "10MB"),
        backup_count=config.get("backup_count", 5),
        json_format=config.get("json_format", False),
        console_output=config.get("console_output", True)
    )

