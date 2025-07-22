"""
Agent Client

Client for integrating the content approval interface with the enhanced
social media agent system.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the enhanced system directly for local integration
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from main_enhanced import EnhancedSocialMediaAgentSystem


class AgentClient:
    """
    Client for communicating with the enhanced social media agent system.
    
    This client can work in two modes:
    1. Direct integration (when running in the same process)
    2. HTTP API integration (when running as separate services)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the agent client."""
        self.config = config
        self.logger = logging.getLogger("agent_client")
        
        # Configuration
        self.integration_mode = config.get('integration_mode', 'direct')  # 'direct' or 'api'
        self.api_base_url = config.get('api_base_url', 'http://localhost:8000')
        
        # Direct integration
        self.agent_system = None
        if self.integration_mode == 'direct':
            self.agent_system = EnhancedSocialMediaAgentSystem(
                config.get('agent_config_path')
            )
        
        # HTTP session for API mode
        self.session = None
        
        self.logger.info(f"Agent client initialized in {self.integration_mode} mode")
    
    async def start(self):
        """Start the agent client."""
        try:
            if self.integration_mode == 'direct':
                if self.agent_system:
                    await self.agent_system.start()
                    self.logger.info("Direct agent system started")
            else:
                # Initialize HTTP session for API mode
                self.session = aiohttp.ClientSession()
                self.logger.info("HTTP session initialized for API mode")
                
        except Exception as e:
            self.logger.error(f"Error starting agent client: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the agent client."""
        try:
            if self.integration_mode == 'direct':
                if self.agent_system:
                    await self.agent_system.stop()
                    self.logger.info("Direct agent system stopped")
            else:
                if self.session:
                    await self.session.close()
                    self.logger.info("HTTP session closed")
                    
        except Exception as e:
            self.logger.error(f"Error stopping agent client: {str(e)}")
    
    async def create_content_campaign(self, campaign_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new content campaign.
        
        Args:
            campaign_request: Campaign requirements and parameters
            
        Returns:
            Campaign creation result with content suggestions
        """
        try:
            if self.integration_mode == 'direct':
                return await self.agent_system.create_content_campaign(campaign_request)
            else:
                return await self._api_request('POST', '/campaigns', campaign_request)
                
        except Exception as e:
            self.logger.error(f"Error creating content campaign: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_content_approval(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content approval decisions.
        
        Args:
            approval_data: Approval decisions for content suggestions
            
        Returns:
            Processing result and next steps
        """
        try:
            if self.integration_mode == 'direct':
                return await self.agent_system.process_content_approval(approval_data)
            else:
                return await self._api_request('POST', '/approvals', approval_data)
                
        except Exception as e:
            self.logger.error(f"Error processing content approval: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_content_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get content improvement recommendations.
        
        Args:
            request_data: Request parameters for recommendations
            
        Returns:
            Content recommendations and optimization suggestions
        """
        try:
            if self.integration_mode == 'direct':
                return await self.agent_system.get_content_recommendations(request_data)
            else:
                return await self._api_request('POST', '/recommendations', request_data)
                
        except Exception as e:
            self.logger.error(f"Error getting content recommendations: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            if self.integration_mode == 'direct':
                return await self.agent_system.get_system_status()
            else:
                return await self._api_request('GET', '/status')
                
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_performance_report(self, report_type: str = 'weekly') -> Dict[str, Any]:
        """
        Generate performance report.
        
        Args:
            report_type: Type of report (daily, weekly, monthly)
            
        Returns:
            Performance report
        """
        try:
            if self.integration_mode == 'direct':
                return await self.agent_system.generate_performance_report(report_type)
            else:
                return await self._api_request('GET', f'/reports/{report_type}')
                
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get status of a specific campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Campaign status information
        """
        try:
            if self.integration_mode == 'direct':
                # For direct mode, we need to access the team leader's campaign data
                if (self.agent_system and 
                    self.agent_system.team_leader and 
                    campaign_id in self.agent_system.team_leader.active_campaigns):
                    
                    campaign = self.agent_system.team_leader.active_campaigns[campaign_id]
                    return {
                        'success': True,
                        'campaign': campaign
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Campaign not found'
                    }
            else:
                return await self._api_request('GET', f'/campaigns/{campaign_id}')
                
        except Exception as e:
            self.logger.error(f"Error getting campaign status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_pending_approvals(self) -> Dict[str, Any]:
        """Get list of campaigns pending approval."""
        try:
            if self.integration_mode == 'direct':
                if (self.agent_system and 
                    self.agent_system.team_leader):
                    
                    pending_approvals = self.agent_system.team_leader.pending_approvals
                    return {
                        'success': True,
                        'pending_approvals': pending_approvals
                    }
                else:
                    return {
                        'success': False,
                        'error': 'System not available'
                    }
            else:
                return await self._api_request('GET', '/approvals/pending')
                
        except Exception as e:
            self.logger.error(f"Error getting pending approvals: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _api_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an API request to the agent system.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            API response
        """
        if not self.session:
            return {
                'success': False,
                'error': 'HTTP session not initialized'
            }
        
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url) as response:
                    return await response.json()
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    return await response.json()
            elif method.upper() == 'PUT':
                async with self.session.put(url, json=data) as response:
                    return await response.json()
            elif method.upper() == 'DELETE':
                async with self.session.delete(url) as response:
                    return await response.json()
            else:
                return {
                    'success': False,
                    'error': f'Unsupported HTTP method: {method}'
                }
                
        except aiohttp.ClientError as e:
            return {
                'success': False,
                'error': f'HTTP request failed: {str(e)}'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }


# Example usage and testing functions
async def test_agent_client():
    """Test the agent client functionality."""
    config = {
        'integration_mode': 'direct',
        'agent_config_path': None  # Use default config
    }
    
    client = AgentClient(config)
    
    try:
        # Start the client
        await client.start()
        
        # Test system status
        status = await client.get_system_status()
        print(f"System Status: {status}")
        
        # Test creating a campaign
        campaign_request = {
            'name': 'Test Campaign',
            'business_info': {
                'name': 'Test Business',
                'industry': 'Technology',
                'target_audience': 'Tech enthusiasts',
                'brand_voice': 'Professional and innovative'
            },
            'platforms': ['facebook', 'twitter'],
            'content_count': 5,
            'content_types': ['educational', 'promotional'],
            'objectives': ['engagement', 'brand_awareness']
        }
        
        campaign_result = await client.create_content_campaign(campaign_request)
        print(f"Campaign Creation: {campaign_result}")
        
        if campaign_result.get('success'):
            campaign_id = campaign_result['campaign']['id']
            
            # Test approval process
            approval_data = {
                'campaign_id': campaign_id,
                'approvals': {}
            }
            
            # Approve first content suggestion
            if campaign_result['content_suggestions']:
                first_suggestion = campaign_result['content_suggestions'][0]
                approval_data['approvals'][first_suggestion['id']] = {
                    'action': 'approve',
                    'comments': 'Looks good!'
                }
            
            approval_result = await client.process_content_approval(approval_data)
            print(f"Approval Processing: {approval_result}")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
    finally:
        await client.stop()


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_agent_client())

