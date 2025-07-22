"""
Social Media Agent System

An open-source, AI-powered social media management system with autonomous agents.
"""

__version__ = "1.0.0"
__author__ = "Manus AI"
__email__ = "contact@manus.ai"
__license__ = "MIT"

from .agents.base_agent import BaseAgent
from .agents.team_leader.team_leader import TeamLeader
from .config.config_manager import ConfigManager
from .utils.logger import get_logger

__all__ = [
    "BaseAgent",
    "TeamLeader", 
    "ConfigManager",
    "get_logger",
]

