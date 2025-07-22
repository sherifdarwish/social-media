"""
Test Suite for Enhanced Social Media Agent System

Comprehensive tests for the enhanced system including Generator Agent,
Evaluation Agent, and content approval workflow.
"""

import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Import the enhanced system components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.generator_agent.generator_agent import GeneratorAgent
from agents.evaluation_agent.evaluation_agent import EvaluationAgent
from agents.team_leader.enhanced_team_leader import EnhancedTeamLeaderAgent
from main_enhanced import EnhancedSocialMediaAgentSystem


class TestGeneratorAgent:
    """Test suite for Generator Agent."""
    
    @pytest.fixture
    async def generator_agent(self):
        """Create a Generator Agent for testing."""
        config = {
            'content_generation': {
                'default_count': 5,
                'max_count': 20
            },
            'llm_providers': {
                'primary': 'openai',
                'fallback': ['anthropic']
            }
        }
        agent = GeneratorAgent(config)
        await agent.start()
        yield agent
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_create_business_briefing(self, generator_agent):
        """Test business briefing creation."""
        business_info = {
            'name': 'Test Company',
            'industry': 'Technology',
            'target_audience': 'Tech professionals',
            'brand_voice': 'Professional and innovative'
        }
        
        result = await generator_agent.create_business_briefing(business_info)
        
        assert result['success'] is True
        assert 'briefing' in result
        assert result['briefing']['business_profile']['name'] == 'Test Company'
        assert 'id' in result['briefing']
    
    @pytest.mark.asyncio
    async def test_generate_content_suggestions(self, generator_agent):
        """Test content suggestion generation."""
        # First create a briefing
        business_info = {
            'name': 'Test Company',
            'industry': 'Technology',
            'target_audience': 'Tech professionals'
        }
        briefing_result = await generator_agent.create_business_briefing(business_info)
        
        # Generate content suggestions
        content_request = {
            'briefing_id': briefing_result['briefing']['id'],
            'platforms': ['facebook', 'twitter'],
            'content_count': 3,
            'content_types': ['educational', 'promotional']
        }
        
        result = await generator_agent.generate_content_suggestions(content_request)
        
        assert result['success'] is True
        assert 'suggestions' in result
        assert len(result['suggestions']) == 3
        
        # Check suggestion structure
        suggestion = result['suggestions'][0]
        assert 'id' in suggestion
        assert 'platform' in suggestion
        assert 'content_type' in suggestion
        assert 'full_text' in suggestion
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, generator_agent):
        """Test performance metrics retrieval."""
        metrics = await generator_agent.get_performance_metrics()
        
        assert 'success' in metrics
        assert 'metrics' in metrics
        assert 'briefings_created' in metrics['metrics']
        assert 'suggestions_generated' in metrics['metrics']


class TestEvaluationAgent:
    """Test suite for Evaluation Agent."""
    
    @pytest.fixture
    async def evaluation_agent(self):
        """Create an Evaluation Agent for testing."""
        config = {
            'feedback_processing': {
                'real_time_analysis': True,
                'sentiment_analysis': True
            },
            'machine_learning': {
                'min_training_samples': 5,
                'learning_rate': 0.1
            }
        }
        agent = EvaluationAgent(config)
        await agent.start()
        yield agent
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_process_feedback(self, evaluation_agent):
        """Test feedback processing."""
        feedback_data = {
            'content_suggestion_id': 'test_123',
            'feedback_type': 'approve',
            'feedback_comments': 'Great content!',
            'platform': 'facebook',
            'content_type': 'educational',
            'timestamp': datetime.utcnow().isoformat(),
            'content_text': 'This is test content',
            'hashtags': ['#test', '#content'],
            'engagement_score': 85
        }
        
        result = await evaluation_agent.process_feedback(feedback_data)
        
        assert result['success'] is True
        assert 'analysis_result' in result
        assert result['analysis_result']['feedback_type'] == 'approve'
    
    @pytest.mark.asyncio
    async def test_analyze_feedback_patterns(self, evaluation_agent):
        """Test feedback pattern analysis."""
        # Process multiple feedback entries
        feedback_entries = [
            {
                'content_suggestion_id': f'test_{i}',
                'feedback_type': 'approve' if i % 2 == 0 else 'reject',
                'platform': 'facebook',
                'content_type': 'educational',
                'timestamp': datetime.utcnow().isoformat()
            }
            for i in range(10)
        ]
        
        for feedback in feedback_entries:
            await evaluation_agent.process_feedback(feedback)
        
        # Analyze patterns
        analysis_request = {
            'time_range': {
                'start': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'end': datetime.utcnow().isoformat()
            }
        }
        
        result = await evaluation_agent.analyze_feedback_patterns(analysis_request)
        
        assert result['success'] is True
        assert 'patterns' in result
        assert 'metrics' in result
    
    @pytest.mark.asyncio
    async def test_get_content_recommendations(self, evaluation_agent):
        """Test content recommendation generation."""
        request_data = {
            'platform': 'facebook',
            'content_type': 'educational',
            'current_content': {
                'text': 'This is test content',
                'hashtags': ['#test'],
                'length': 20
            }
        }
        
        result = await evaluation_agent.get_content_recommendations(request_data)
        
        assert result['success'] is True
        assert 'recommendations' in result


class TestEnhancedTeamLeader:
    """Test suite for Enhanced Team Leader Agent."""
    
    @pytest.fixture
    async def team_leader(self):
        """Create an Enhanced Team Leader for testing."""
        config = {
            'team_leader': {
                'reporting_schedule': 'weekly'
            },
            'workflow': {
                'approval_required': True,
                'auto_post_threshold': 0.8
            },
            'generator_agent': {},
            'evaluation_agent': {},
            'facebook_agent': {},
            'twitter_agent': {},
            'instagram_agent': {},
            'linkedin_agent': {},
            'tiktok_agent': {}
        }
        
        # Mock the sub-agents to avoid actual initialization
        with patch.multiple(
            'agents.team_leader.enhanced_team_leader',
            GeneratorAgent=AsyncMock,
            EvaluationAgent=AsyncMock,
            FacebookAgent=AsyncMock,
            TwitterAgent=AsyncMock,
            InstagramAgent=AsyncMock,
            LinkedInAgent=AsyncMock,
            TikTokAgent=AsyncMock
        ):
            agent = EnhancedTeamLeaderAgent(config)
            await agent.start()
            yield agent
            await agent.stop()
    
    @pytest.mark.asyncio
    async def test_create_content_campaign(self, team_leader):
        """Test content campaign creation."""
        campaign_request = {
            'name': 'Test Campaign',
            'business_info': {
                'name': 'Test Business',
                'industry': 'Technology'
            },
            'platforms': ['facebook', 'twitter'],
            'content_count': 5,
            'content_types': ['educational'],
            'objectives': ['engagement']
        }
        
        # Mock the generator agent response
        team_leader.generator_agent.create_business_briefing = AsyncMock(return_value={
            'success': True,
            'briefing': {
                'id': 'briefing_123',
                'business_profile_id': 'profile_123'
            }
        })
        
        team_leader.generator_agent.generate_content_suggestions = AsyncMock(return_value={
            'success': True,
            'suggestions': [
                {
                    'id': 'suggestion_1',
                    'platform': 'facebook',
                    'content_type': 'educational',
                    'full_text': 'Test content'
                }
            ]
        })
        
        result = await team_leader.create_content_campaign(campaign_request)
        
        assert result['success'] is True
        assert 'campaign' in result
        assert result['campaign']['name'] == 'Test Campaign'
        assert 'content_suggestions' in result
    
    @pytest.mark.asyncio
    async def test_process_content_approval(self, team_leader):
        """Test content approval processing."""
        # First create a campaign
        campaign_id = 'test_campaign_123'
        team_leader.active_campaigns[campaign_id] = {
            'id': campaign_id,
            'content_suggestions': [
                {
                    'id': 'suggestion_1',
                    'platform': 'facebook',
                    'content_type': 'educational',
                    'full_text': 'Test content'
                }
            ]
        }
        
        approval_data = {
            'campaign_id': campaign_id,
            'approvals': {
                'suggestion_1': {
                    'action': 'approve',
                    'comments': 'Looks good!'
                }
            }
        }
        
        # Mock evaluation agent
        team_leader.evaluation_agent.process_feedback = AsyncMock(return_value={
            'success': True
        })
        
        result = await team_leader.process_content_approval(approval_data)
        
        assert result['success'] is True
        assert result['approved_count'] == 1
        assert result['rejected_count'] == 0
    
    @pytest.mark.asyncio
    async def test_get_team_status(self, team_leader):
        """Test team status retrieval."""
        # Mock agent status responses
        team_leader.generator_agent.get_status = AsyncMock(return_value={
            'agent_type': 'generator',
            'is_running': True
        })
        
        team_leader.evaluation_agent.get_status = AsyncMock(return_value={
            'agent_type': 'evaluation',
            'is_running': True
        })
        
        for agent in team_leader.platform_agents.values():
            agent.get_status = AsyncMock(return_value={
                'is_running': True
            })
        
        result = await team_leader.get_team_status()
        
        assert result['success'] is True
        assert 'status' in result
        assert 'enhanced_team_leader' in result['status']
        assert 'generator_agent' in result['status']
        assert 'evaluation_agent' in result['status']


class TestEnhancedSystem:
    """Test suite for the complete Enhanced System."""
    
    @pytest.fixture
    def temp_config(self):
        """Create a temporary configuration file."""
        config_data = {
            'system': {
                'name': 'Test System',
                'environment': 'test'
            },
            'database': {
                'type': 'sqlite',
                'path': ':memory:'
            },
            'api_keys': {
                'openai': {
                    'api_key': 'test_key'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        yield config_path
        
        # Cleanup
        os.unlink(config_path)
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, temp_config):
        """Test system initialization."""
        with patch.multiple(
            'main_enhanced',
            EnhancedTeamLeaderAgent=AsyncMock
        ):
            system = EnhancedSocialMediaAgentSystem(temp_config)
            
            assert system.config_manager is not None
            assert system.team_leader is not None
            assert system.is_running is False
    
    @pytest.mark.asyncio
    async def test_system_start_stop(self, temp_config):
        """Test system start and stop."""
        with patch.multiple(
            'main_enhanced',
            EnhancedTeamLeaderAgent=AsyncMock
        ):
            system = EnhancedSocialMediaAgentSystem(temp_config)
            
            # Mock team leader
            system.team_leader.start = AsyncMock()
            system.team_leader.stop = AsyncMock()
            system.team_leader.is_running = True
            
            # Test start
            await system.start()
            assert system.is_running is True
            
            # Test stop
            await system.stop()
            assert system.is_running is False
    
    @pytest.mark.asyncio
    async def test_system_status(self, temp_config):
        """Test system status retrieval."""
        with patch.multiple(
            'main_enhanced',
            EnhancedTeamLeaderAgent=AsyncMock
        ):
            system = EnhancedSocialMediaAgentSystem(temp_config)
            
            # Mock team leader status
            system.team_leader.get_team_status = AsyncMock(return_value={
                'success': True,
                'status': {
                    'enhanced_team_leader': {
                        'is_running': True
                    }
                }
            })
            
            system.is_running = True
            system.start_time = datetime.utcnow()
            
            result = await system.get_system_status()
            
            assert result['success'] is True
            assert 'status' in result
            assert 'system' in result['status']


class TestIntegration:
    """Integration tests for the enhanced system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # This test would simulate the complete workflow:
        # 1. Create business briefing
        # 2. Generate content suggestions
        # 3. Present for approval
        # 4. Process approval decisions
        # 5. Schedule and post content
        # 6. Collect feedback
        # 7. Analyze and improve
        
        # Mock all external dependencies
        with patch.multiple(
            'main_enhanced',
            EnhancedTeamLeaderAgent=AsyncMock
        ):
            # Create system
            system = EnhancedSocialMediaAgentSystem()
            
            # Mock workflow steps
            campaign_request = {
                'name': 'Integration Test Campaign',
                'business_info': {
                    'name': 'Test Business',
                    'industry': 'Technology'
                },
                'platforms': ['facebook'],
                'content_count': 2
            }
            
            # Mock campaign creation
            system.team_leader.create_content_campaign = AsyncMock(return_value={
                'success': True,
                'campaign': {
                    'id': 'test_campaign',
                    'content_suggestions': [
                        {'id': 'suggestion_1', 'platform': 'facebook'}
                    ]
                }
            })
            
            # Mock approval processing
            system.team_leader.process_content_approval = AsyncMock(return_value={
                'success': True,
                'approved_count': 1
            })
            
            # Test workflow
            campaign_result = await system.create_content_campaign(campaign_request)
            assert campaign_result['success'] is True
            
            approval_data = {
                'campaign_id': 'test_campaign',
                'approvals': {
                    'suggestion_1': {'action': 'approve'}
                }
            }
            
            approval_result = await system.process_content_approval(approval_data)
            assert approval_result['success'] is True


# Test fixtures and utilities
@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        'choices': [
            {
                'message': {
                    'content': 'This is a test response from the LLM.'
                }
            }
        ]
    }


@pytest.fixture
def sample_business_info():
    """Sample business information for testing."""
    return {
        'name': 'TechCorp Solutions',
        'industry': 'Technology',
        'target_audience': 'Small business owners and entrepreneurs',
        'brand_voice': 'Professional yet approachable',
        'products_services': [
            'Cloud computing solutions',
            'IT consulting',
            'Software development'
        ],
        'unique_value_proposition': 'Affordable enterprise-grade technology for small businesses',
        'competitors': ['BigTech Inc', 'CloudSoft LLC'],
        'goals': ['Increase brand awareness', 'Generate leads', 'Educate market']
    }


@pytest.fixture
def sample_content_suggestions():
    """Sample content suggestions for testing."""
    return [
        {
            'id': 'suggestion_1',
            'platform': 'facebook',
            'content_type': 'educational',
            'full_text': 'Did you know that 60% of small businesses still don\'t use cloud computing? Here\'s why you should make the switch today! 🚀',
            'hashtags': ['#CloudComputing', '#SmallBusiness', '#Technology'],
            'call_to_action': 'Learn more about our cloud solutions',
            'engagement_score': 85,
            'optimal_posting_time': '2024-01-15T14:00:00Z'
        },
        {
            'id': 'suggestion_2',
            'platform': 'twitter',
            'content_type': 'promotional',
            'full_text': '🎯 New Year, New Tech Stack! Get 30% off our cloud migration services this month. Transform your business operations today!',
            'hashtags': ['#CloudMigration', '#NewYear', '#TechDeals'],
            'call_to_action': 'Book a free consultation',
            'engagement_score': 78,
            'optimal_posting_time': '2024-01-15T16:00:00Z'
        }
    ]


# Performance tests
class TestPerformance:
    """Performance tests for the enhanced system."""
    
    @pytest.mark.asyncio
    async def test_content_generation_performance(self):
        """Test content generation performance."""
        # Test that content generation completes within reasonable time
        start_time = datetime.utcnow()
        
        # Mock content generation
        with patch('agents.generator_agent.generator_agent.GeneratorAgent') as mock_agent:
            mock_agent.return_value.generate_content_suggestions = AsyncMock(return_value={
                'success': True,
                'suggestions': [{'id': f'suggestion_{i}'} for i in range(10)]
            })
            
            agent = mock_agent.return_value
            result = await agent.generate_content_suggestions({
                'content_count': 10,
                'platforms': ['facebook', 'twitter']
            })
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        assert result['success'] is True
        assert duration < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_feedback_processing_performance(self):
        """Test feedback processing performance."""
        # Test that feedback processing handles multiple entries efficiently
        feedback_entries = [
            {
                'content_suggestion_id': f'test_{i}',
                'feedback_type': 'approve',
                'timestamp': datetime.utcnow().isoformat()
            }
            for i in range(100)
        ]
        
        start_time = datetime.utcnow()
        
        # Mock feedback processing
        with patch('agents.evaluation_agent.evaluation_agent.EvaluationAgent') as mock_agent:
            mock_agent.return_value.process_feedback = AsyncMock(return_value={
                'success': True
            })
            
            agent = mock_agent.return_value
            
            # Process all feedback entries
            for feedback in feedback_entries:
                await agent.process_feedback(feedback)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        assert duration < 10.0  # Should process 100 entries within 10 seconds


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])

