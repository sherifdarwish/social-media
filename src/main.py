#!/usr/bin/env python3
"""
Social Media Agent - Main Application Entry Point

This module provides the main entry point for the Social Media Agent system,
including the primary SocialMediaAgent class and command-line interface.
"""

import asyncio
import argparse
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.config.config_manager import ConfigManager
from src.config.api_key_manager import APIKeyManager
from src.content_generation.content_generator import ContentGenerator
from src.metrics.metrics_collector import MetricsCollector
from src.agents.team_leader.team_leader import TeamLeader
from src.agents.platform_agents.facebook_agent import FacebookAgent
from src.agents.platform_agents.twitter_agent import TwitterAgent
from src.agents.platform_agents.instagram_agent import InstagramAgent
from src.agents.platform_agents.linkedin_agent import LinkedInAgent
from src.agents.platform_agents.tiktok_agent import TikTokAgent
from src.utils.logger import setup_logging


class SocialMediaAgent:
    """
    Main Social Media Agent system coordinator.
    
    This class provides the primary interface for managing all platform agents,
    coordinating content creation, and generating reports.
    """
    
    def __init__(self, config_path: str, log_level: str = "INFO"):
        """
        Initialize the social media agent system.
        
        Args:
            config_path (str): Path to the configuration file
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        
        Raises:
            ConfigurationError: If configuration file is invalid
            FileNotFoundError: If configuration file doesn't exist
        """
        self.config_path = config_path
        self.log_level = log_level
        
        # Set up logging
        setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.config_manager = ConfigManager(config_path)
        self.api_key_manager = APIKeyManager(self.config_manager)
        self.content_generator = ContentGenerator(
            self.config_manager, 
            self.api_key_manager
        )
        self.metrics_collector = MetricsCollector(self.config_manager)
        
        # Initialize team leader
        self.team_leader = TeamLeader(
            config_manager=self.config_manager,
            content_generator=self.content_generator,
            metrics_collector=self.metrics_collector
        )
        
        # Initialize platform agents
        self.agents = {}
        self._initialize_agents()
        
        # System state
        self.is_running = False
        self.start_time = None
        
        self.logger.info("Social Media Agent initialized successfully")
    
    def _initialize_agents(self):
        """Initialize all platform agents based on configuration."""
        platform_configs = self.config_manager.get_section("platforms")
        
        agent_classes = {
            "facebook": FacebookAgent,
            "twitter": TwitterAgent,
            "instagram": InstagramAgent,
            "linkedin": LinkedInAgent,
            "tiktok": TikTokAgent
        }
        
        for platform, config in platform_configs.items():
            if config.get("enabled", False):
                agent_class = agent_classes.get(platform)
                if agent_class:
                    try:
                        agent = agent_class(
                            name=f"{platform}_agent",
                            platform=platform,
                            config_manager=self.config_manager,
                            content_generator=self.content_generator,
                            metrics_collector=self.metrics_collector,
                            config=config
                        )
                        self.agents[platform] = agent
                        self.team_leader.register_agent(agent)
                        self.logger.info(f"Initialized {platform} agent")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize {platform} agent: {e}")
                else:
                    self.logger.warning(f"Unknown platform: {platform}")
    
    async def start_all_agents(self) -> bool:
        """
        Start all configured platform agents.
        
        Returns:
            bool: True if all agents started successfully, False otherwise
        """
        self.logger.info("Starting all platform agents...")
        
        try:
            # Start team leader first
            await self.team_leader.start()
            
            # Start all platform agents
            start_results = []
            for platform, agent in self.agents.items():
                try:
                    result = await agent.start()
                    start_results.append(result)
                    if result:
                        self.logger.info(f"✅ {platform} agent started successfully")
                    else:
                        self.logger.error(f"❌ Failed to start {platform} agent")
                except Exception as e:
                    self.logger.error(f"❌ Error starting {platform} agent: {e}")
                    start_results.append(False)
            
            # Check if all agents started successfully
            all_started = all(start_results)
            
            if all_started:
                self.is_running = True
                self.start_time = datetime.utcnow()
                self.logger.info("🚀 All agents started successfully!")
            else:
                self.logger.warning("⚠️  Some agents failed to start")
            
            return all_started
            
        except Exception as e:
            self.logger.error(f"Failed to start agents: {e}")
            return False
    
    async def stop_all_agents(self) -> bool:
        """
        Stop all running platform agents.
        
        Returns:
            bool: True if all agents stopped successfully, False otherwise
        """
        self.logger.info("Stopping all platform agents...")
        
        try:
            # Stop all platform agents
            stop_results = []
            for platform, agent in self.agents.items():
                try:
                    result = await agent.stop()
                    stop_results.append(result)
                    if result:
                        self.logger.info(f"✅ {platform} agent stopped successfully")
                    else:
                        self.logger.error(f"❌ Failed to stop {platform} agent")
                except Exception as e:
                    self.logger.error(f"❌ Error stopping {platform} agent: {e}")
                    stop_results.append(False)
            
            # Stop team leader
            await self.team_leader.stop()
            
            # Check if all agents stopped successfully
            all_stopped = all(stop_results)
            
            if all_stopped:
                self.is_running = False
                self.logger.info("🛑 All agents stopped successfully!")
            else:
                self.logger.warning("⚠️  Some agents failed to stop properly")
            
            return all_stopped
            
        except Exception as e:
            self.logger.error(f"Failed to stop agents: {e}")
            return False
    
    async def create_coordinated_post(
        self, 
        content_brief: str, 
        platforms: Optional[List[str]] = None,
        content_type: str = "text",
        schedule_time: Optional[datetime] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create and post content across specified platforms.
        
        Args:
            content_brief (str): Brief description of content to create
            platforms (List[str], optional): List of platforms to post to.
                If None, posts to all enabled platforms.
            content_type (str): Type of content ("text", "image", "video")
            schedule_time (datetime, optional): When to post the content.
                If None, posts immediately.
            **kwargs: Additional parameters for content generation
        
        Returns:
            Dict[str, Any]: Results for each platform
        """
        if not self.is_running:
            raise RuntimeError("Agents are not running. Call start_all_agents() first.")
        
        # Use all enabled platforms if none specified
        if platforms is None:
            platforms = list(self.agents.keys())
        
        # Filter to only include available platforms
        available_platforms = [p for p in platforms if p in self.agents]
        
        if not available_platforms:
            raise ValueError("No available platforms specified")
        
        self.logger.info(f"Creating coordinated post for platforms: {available_platforms}")
        
        # Delegate to team leader for coordination
        return await self.team_leader.create_coordinated_post(
            content_brief=content_brief,
            platforms=available_platforms,
            content_type=content_type,
            schedule_time=schedule_time,
            **kwargs
        )
    
    async def generate_weekly_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "html"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive weekly performance report.
        
        Args:
            start_date (datetime, optional): Start date for report period
            end_date (datetime, optional): End date for report period
            format (str): Output format ("html", "pdf", "json", "markdown")
        
        Returns:
            Dict[str, Any]: Report data and metadata
        """
        if not self.is_running:
            raise RuntimeError("Agents are not running. Call start_all_agents() first.")
        
        self.logger.info("Generating weekly report...")
        
        # Delegate to team leader
        return await self.team_leader.generate_weekly_report(
            start_date=start_date,
            end_date=end_date,
            format=format
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status and health information.
        
        Returns:
            Dict[str, Any]: System status including agent states, metrics, and health
        """
        uptime = None
        if self.start_time:
            uptime = str(datetime.utcnow() - self.start_time)
        
        active_agents = []
        agent_statuses = {}
        
        for platform, agent in self.agents.items():
            status = agent.get_status()
            agent_statuses[platform] = status
            if status.get("status") == "running":
                active_agents.append(platform)
        
        return {
            "is_running": self.is_running,
            "uptime": uptime,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "active_agents": active_agents,
            "total_agents": len(self.agents),
            "agent_statuses": agent_statuses,
            "team_leader_status": self.team_leader.get_status() if hasattr(self.team_leader, 'get_status') else "unknown"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive system health check.
        
        Returns:
            Dict[str, Any]: Health check results for all components
        """
        health_results = {}
        
        # Check team leader health
        try:
            team_leader_health = await self.team_leader.health_check()
            health_results["team_leader"] = team_leader_health
        except Exception as e:
            health_results["team_leader"] = {"healthy": False, "error": str(e)}
        
        # Check each agent's health
        for platform, agent in self.agents.items():
            try:
                agent_health = await agent.health_check()
                health_results[platform] = agent_health
            except Exception as e:
                health_results[platform] = {"healthy": False, "error": str(e)}
        
        # Check core components
        try:
            # Test configuration
            config_errors = self.config_manager.validate_config()
            health_results["configuration"] = {
                "healthy": len(config_errors) == 0,
                "errors": config_errors
            }
            
            # Test API keys
            api_key_status = {}
            for provider in ["openai", "anthropic", "google"]:
                try:
                    key = self.api_key_manager.get_api_key(provider)
                    api_key_status[provider] = {"available": key is not None}
                except Exception as e:
                    api_key_status[provider] = {"available": False, "error": str(e)}
            
            health_results["api_keys"] = api_key_status
            
        except Exception as e:
            health_results["core_components"] = {"healthy": False, "error": str(e)}
        
        return health_results
    
    async def run_automation_loop(self):
        """
        Run the main automation loop for scheduled content creation.
        """
        self.logger.info("Starting automation loop...")
        
        try:
            while self.is_running:
                # Let team leader handle automation
                await self.team_leader.run_automation_cycle()
                
                # Wait before next cycle (configurable)
                automation_config = self.config_manager.get_section("automation")
                cycle_interval = automation_config.get("cycle_interval_minutes", 60)
                await asyncio.sleep(cycle_interval * 60)
                
        except asyncio.CancelledError:
            self.logger.info("Automation loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in automation loop: {e}")
            raise


async def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Social Media Agent System")
    parser.add_argument(
        "--config", 
        default="config/config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--mode",
        default="interactive",
        choices=["interactive", "automation", "daemon"],
        help="Run mode"
    )
    parser.add_argument(
        "--post",
        help="Create a single post with the given content brief"
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        help="Platforms to post to (when using --post)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate weekly report and exit"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and exit"
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Perform health check and exit"
    )
    
    args = parser.parse_args()
    
    # Initialize the agent
    try:
        agent = SocialMediaAgent(args.config, args.log_level)
    except Exception as e:
        print(f"Failed to initialize Social Media Agent: {e}")
        sys.exit(1)
    
    # Handle different modes
    if args.status:
        # Show status and exit
        status = agent.get_system_status()
        print("📊 System Status:")
        print(f"  Running: {status['is_running']}")
        print(f"  Uptime: {status['uptime'] or 'Not started'}")
        print(f"  Active Agents: {len(status['active_agents'])}/{status['total_agents']}")
        for platform, agent_status in status['agent_statuses'].items():
            emoji = "✅" if agent_status.get('status') == 'running' else "❌"
            print(f"    {emoji} {platform}: {agent_status.get('status', 'unknown')}")
        return
    
    if args.health:
        # Perform health check and exit
        print("🏥 Performing health check...")
        health = await agent.health_check()
        
        overall_healthy = True
        for component, health_info in health.items():
            is_healthy = health_info.get("healthy", False)
            overall_healthy = overall_healthy and is_healthy
            emoji = "✅" if is_healthy else "❌"
            print(f"  {emoji} {component}: {'Healthy' if is_healthy else 'Unhealthy'}")
            if not is_healthy and "error" in health_info:
                print(f"      Error: {health_info['error']}")
        
        print(f"\n🎯 Overall Status: {'Healthy' if overall_healthy else 'Unhealthy'}")
        sys.exit(0 if overall_healthy else 1)
    
    # Start agents
    print("🚀 Starting Social Media Agent...")
    success = await agent.start_all_agents()
    
    if not success:
        print("❌ Failed to start all agents")
        sys.exit(1)
    
    try:
        if args.post:
            # Create a single post
            print(f"📝 Creating post: {args.post}")
            result = await agent.create_coordinated_post(
                content_brief=args.post,
                platforms=args.platforms
            )
            
            print("📊 Post Results:")
            for platform, post_result in result.items():
                if post_result.success:
                    print(f"  ✅ {platform}: {post_result.post_id}")
                else:
                    print(f"  ❌ {platform}: {post_result.error_message}")
        
        elif args.report:
            # Generate report
            print("📊 Generating weekly report...")
            report = await agent.generate_weekly_report()
            print(f"✅ Report generated: {report.get('file_path', 'report.html')}")
        
        elif args.mode == "automation":
            # Run automation mode
            print("🤖 Running in automation mode...")
            print("Press Ctrl+C to stop")
            
            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                print("\n🛑 Received shutdown signal...")
                raise KeyboardInterrupt
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            await agent.run_automation_loop()
        
        elif args.mode == "interactive":
            # Interactive mode
            print("💬 Running in interactive mode...")
            print("Available commands:")
            print("  post <content> - Create a post")
            print("  report - Generate weekly report")
            print("  status - Show system status")
            print("  health - Perform health check")
            print("  quit - Exit the application")
            
            while True:
                try:
                    command = input("\n> ").strip().split()
                    if not command:
                        continue
                    
                    if command[0] == "quit":
                        break
                    elif command[0] == "post" and len(command) > 1:
                        content = " ".join(command[1:])
                        result = await agent.create_coordinated_post(content)
                        for platform, post_result in result.items():
                            status = "✅" if post_result.success else "❌"
                            print(f"  {status} {platform}")
                    elif command[0] == "report":
                        report = await agent.generate_weekly_report()
                        print(f"Report generated: {report.get('file_path')}")
                    elif command[0] == "status":
                        status = agent.get_system_status()
                        print(f"Active agents: {len(status['active_agents'])}")
                    elif command[0] == "health":
                        health = await agent.health_check()
                        healthy_count = sum(1 for h in health.values() if h.get("healthy", False))
                        print(f"Healthy components: {healthy_count}/{len(health)}")
                    else:
                        print("Unknown command")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    
    finally:
        # Stop all agents
        await agent.stop_all_agents()
        print("👋 Social Media Agent stopped")


if __name__ == "__main__":
    asyncio.run(main())

