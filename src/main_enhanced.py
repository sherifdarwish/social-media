"""
Enhanced Social Media Agent System

Main application entry point for the enhanced social media agent system
with Generator Agent and Evaluation Agent integration.
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any
from datetime import datetime

from src.config.config_manager import ConfigManager
from src.agents.team_leader.enhanced_team_leader import EnhancedTeamLeaderAgent
from src.utils.logger import setup_logging, get_logger


class EnhancedSocialMediaAgentSystem:
    """
    Enhanced Social Media Agent System with content approval workflow.
    
    This system includes:
    1. Generator Agent for content briefing and suggestions
    2. Evaluation Agent for feedback-driven improvements
    3. Enhanced Team Leader for workflow coordination
    4. Platform agents for multi-platform posting
    5. Content approval interface for user feedback
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the enhanced social media agent system."""
        # Setup logging
        setup_logging()
        self.logger = get_logger("enhanced_system")
        
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Initialize enhanced team leader
        self.team_leader = EnhancedTeamLeaderAgent(self.config)
        
        # System state
        self.is_running = False
        self.start_time = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Enhanced Social Media Agent System initialized")
    
    async def start(self):
        """Start the enhanced social media agent system."""
        try:
            self.logger.info("Starting Enhanced Social Media Agent System...")
            self.is_running = True
            self.start_time = datetime.utcnow()
            
            # Start the enhanced team leader (which starts all sub-agents)
            await self.team_leader.start()
            
            self.logger.info("Enhanced Social Media Agent System started successfully")
            
            # Keep the system running
            await self._run_system()
            
        except Exception as e:
            self.logger.error(f"Error starting system: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the enhanced social media agent system."""
        try:
            self.logger.info("Stopping Enhanced Social Media Agent System...")
            self.is_running = False
            
            # Stop the enhanced team leader (which stops all sub-agents)
            if self.team_leader:
                await self.team_leader.stop()
            
            self.logger.info("Enhanced Social Media Agent System stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping system: {str(e)}")
    
    async def create_content_campaign(self, campaign_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new content campaign.
        
        Args:
            campaign_request: Campaign requirements and parameters
            
        Returns:
            Campaign creation result
        """
        if not self.is_running:
            return {
                'success': False,
                'error': 'System is not running'
            }
        
        return await self.team_leader.create_content_campaign(campaign_request)
    
    async def process_content_approval(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content approval decisions.
        
        Args:
            approval_data: Approval decisions for content suggestions
            
        Returns:
            Processing result
        """
        if not self.is_running:
            return {
                'success': False,
                'error': 'System is not running'
            }
        
        return await self.team_leader.process_content_approval(approval_data)
    
    async def get_content_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get content improvement recommendations.
        
        Args:
            request_data: Request parameters for recommendations
            
        Returns:
            Content recommendations
        """
        if not self.is_running:
            return {
                'success': False,
                'error': 'System is not running'
            }
        
        return await self.team_leader.get_content_recommendations(request_data)
    
    async def generate_performance_report(self, report_type: str = 'weekly') -> Dict[str, Any]:
        """
        Generate performance report.
        
        Args:
            report_type: Type of report (daily, weekly, monthly)
            
        Returns:
            Performance report
        """
        if not self.is_running:
            return {
                'success': False,
                'error': 'System is not running'
            }
        
        return await self.team_leader.generate_performance_report(report_type)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            if not self.is_running:
                return {
                    'success': True,
                    'status': {
                        'system': {
                            'is_running': False,
                            'uptime': 0
                        }
                    }
                }
            
            # Get status from team leader
            team_status = await self.team_leader.get_team_status()
            
            # Add system-level information
            system_status = {
                'system': {
                    'is_running': self.is_running,
                    'start_time': self.start_time.isoformat() if self.start_time else None,
                    'uptime': (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0,
                    'config_loaded': bool(self.config),
                    'version': '2.0.0-enhanced'
                }
            }
            
            if team_status.get('success'):
                system_status.update(team_status['status'])
            
            return {
                'success': True,
                'status': system_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _run_system(self):
        """Main system loop."""
        try:
            while self.is_running:
                # System health check
                await self._health_check()
                
                # Sleep for a short interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            self.logger.info("System loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in system loop: {str(e)}")
            self.is_running = False
    
    async def _health_check(self):
        """Perform system health check."""
        try:
            # Check if team leader is still running
            if not self.team_leader.is_running:
                self.logger.warning("Team leader is not running, attempting restart...")
                await self.team_leader.start()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.is_running = False
        
        # Create a task to stop the system
        asyncio.create_task(self.stop())


async def main():
    """Main entry point for the enhanced social media agent system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Social Media Agent System')
    parser.add_argument('--config', '-c', type=str, help='Path to configuration file')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and start the system
    system = EnhancedSocialMediaAgentSystem(args.config)
    
    try:
        await system.start()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
    except Exception as e:
        print(f"System error: {str(e)}")
        sys.exit(1)
    finally:
        await system.stop()


if __name__ == "__main__":
    asyncio.run(main())

