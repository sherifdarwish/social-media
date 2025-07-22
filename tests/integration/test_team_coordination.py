"""
Integration tests for team leader and agent coordination.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.agents.team_leader.team_leader import TeamLeader
from src.agents.team_leader.coordination_system import CoordinationSystem
from src.agents.platform_agents.facebook_agent import FacebookAgent
from src.agents.platform_agents.twitter_agent import TwitterAgent
from src.agents.platform_agents.instagram_agent import InstagramAgent
from src.agents.platform_agents.linkedin_agent import LinkedInAgent
from src.agents.platform_agents.tiktok_agent import TikTokAgent


class TestTeamCoordination:
    """Integration tests for team coordination system."""
    
    @pytest.fixture
    async def team_leader(self, mock_config_manager, mock_content_generator, mock_metrics_collector):
        """Create team leader instance for testing."""
        team_leader = TeamLeader(
            config_manager=mock_config_manager,
            content_generator=mock_content_generator,
            metrics_collector=mock_metrics_collector
        )
        return team_leader
    
    @pytest.fixture
    async def platform_agents(self, mock_config_manager, mock_content_generator, mock_metrics_collector):
        """Create platform agent instances for testing."""
        agents = {}
        
        # Create mock agents for each platform
        platforms = ["facebook", "twitter", "instagram", "linkedin", "tiktok"]
        
        for platform in platforms:
            agent = Mock()
            agent.name = f"{platform}_agent"
            agent.platform = platform
            agent.is_running = False
            agent.status = "stopped"
            
            # Mock agent methods
            async def mock_start():
                agent.is_running = True
                agent.status = "running"
                return True
            
            async def mock_stop():
                agent.is_running = False
                agent.status = "stopped"
                return True
            
            async def mock_create_post(*args, **kwargs):
                return {
                    "success": True,
                    "post_id": f"test_post_{platform}",
                    "content": f"Test content for {platform}"
                }
            
            async def mock_collect_metrics():
                return {
                    "posts_created": 5,
                    "engagement_rate": 3.2,
                    "success_rate": 95.0
                }
            
            agent.start = AsyncMock(side_effect=mock_start)
            agent.stop = AsyncMock(side_effect=mock_stop)
            agent.create_post = AsyncMock(side_effect=mock_create_post)
            agent.collect_metrics = AsyncMock(side_effect=mock_collect_metrics)
            agent.get_status = Mock(return_value={
                "status": "running",
                "posts_today": 3,
                "last_post_time": datetime.utcnow()
            })
            
            agents[platform] = agent
        
        return agents
    
    @pytest.fixture
    async def coordination_system(self, team_leader, platform_agents):
        """Create coordination system with team leader and agents."""
        coordination_system = CoordinationSystem(team_leader)
        
        # Register platform agents
        for platform, agent in platform_agents.items():
            coordination_system.register_agent(agent)
        
        return coordination_system
    
    @pytest.mark.integration
    async def test_team_initialization(self, coordination_system, platform_agents):
        """Test team initialization and agent registration."""
        assert len(coordination_system.agents) == 5
        
        for platform in ["facebook", "twitter", "instagram", "linkedin", "tiktok"]:
            assert platform in coordination_system.agents
            assert coordination_system.agents[platform].platform == platform
    
    @pytest.mark.integration
    async def test_start_all_agents(self, coordination_system, platform_agents):
        """Test starting all platform agents."""
        result = await coordination_system.start_all_agents()
        
        assert result is True
        
        # Verify all agents are running
        for agent in platform_agents.values():
            assert agent.is_running is True
            assert agent.status == "running"
    
    @pytest.mark.integration
    async def test_stop_all_agents(self, coordination_system, platform_agents):
        """Test stopping all platform agents."""
        # Start agents first
        await coordination_system.start_all_agents()
        
        # Stop all agents
        result = await coordination_system.stop_all_agents()
        
        assert result is True
        
        # Verify all agents are stopped
        for agent in platform_agents.values():
            assert agent.is_running is False
            assert agent.status == "stopped"
    
    @pytest.mark.integration
    async def test_coordinated_posting(self, coordination_system, platform_agents):
        """Test coordinated posting across all platforms."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Create coordinated post
        content_brief = "Test coordinated post about social media marketing"
        results = await coordination_system.create_coordinated_post(content_brief)
        
        assert len(results) == 5
        
        # Verify all posts were successful
        for platform, result in results.items():
            assert result["success"] is True
            assert f"test_post_{platform}" in result["post_id"]
    
    @pytest.mark.integration
    async def test_agent_health_monitoring(self, coordination_system, platform_agents):
        """Test agent health monitoring."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Check health of all agents
        health_report = await coordination_system.check_agent_health()
        
        assert "healthy_agents" in health_report
        assert "unhealthy_agents" in health_report
        assert len(health_report["healthy_agents"]) == 5
        assert len(health_report["unhealthy_agents"]) == 0
    
    @pytest.mark.integration
    async def test_metrics_collection_coordination(self, coordination_system, platform_agents):
        """Test coordinated metrics collection."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Collect metrics from all agents
        metrics_report = await coordination_system.collect_all_metrics()
        
        assert len(metrics_report) == 5
        
        # Verify metrics structure
        for platform, metrics in metrics_report.items():
            assert "posts_created" in metrics
            assert "engagement_rate" in metrics
            assert "success_rate" in metrics
    
    @pytest.mark.integration
    async def test_content_strategy_coordination(self, coordination_system, platform_agents):
        """Test content strategy coordination across platforms."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Define content strategy
        strategy = {
            "theme": "productivity_tips",
            "target_audience": "professionals",
            "content_types": ["text", "image"],
            "posting_schedule": {
                "facebook": ["09:00", "15:00"],
                "twitter": ["08:00", "12:00", "18:00"],
                "linkedin": ["07:00", "17:00"],
                "instagram": ["10:00", "16:00"],
                "tiktok": ["19:00"]
            }
        }
        
        # Execute content strategy
        execution_results = await coordination_system.execute_content_strategy(strategy)
        
        assert "scheduled_posts" in execution_results
        assert "execution_summary" in execution_results
        assert execution_results["execution_summary"]["total_posts"] > 0
    
    @pytest.mark.integration
    async def test_error_handling_and_recovery(self, coordination_system, platform_agents):
        """Test error handling and recovery mechanisms."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Simulate agent failure
        platform_agents["facebook"].create_post.side_effect = Exception("Platform API error")
        
        # Attempt coordinated posting
        results = await coordination_system.create_coordinated_post("Test content")
        
        # Verify error handling
        assert results["facebook"]["success"] is False
        assert "error" in results["facebook"]
        
        # Verify other agents still work
        for platform in ["twitter", "instagram", "linkedin", "tiktok"]:
            assert results[platform]["success"] is True
    
    @pytest.mark.integration
    async def test_load_balancing(self, coordination_system, platform_agents):
        """Test load balancing across agents."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Create multiple posts rapidly
        tasks = []
        for i in range(10):
            task = coordination_system.create_coordinated_post(f"Test post {i}")
            tasks.append(task)
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify load distribution
        successful_posts = 0
        for result in results:
            if isinstance(result, dict):
                successful_posts += sum(1 for r in result.values() if r.get("success", False))
        
        assert successful_posts > 0
    
    @pytest.mark.integration
    async def test_cross_platform_consistency(self, coordination_system, platform_agents):
        """Test content consistency across platforms."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Create content with brand consistency requirements
        brand_guidelines = {
            "tone": "professional",
            "hashtags": ["#socialmedia", "#marketing"],
            "mention_brand": True,
            "call_to_action": "Visit our website"
        }
        
        results = await coordination_system.create_branded_content(
            "New product launch announcement",
            brand_guidelines
        )
        
        # Verify brand consistency
        for platform, result in results.items():
            assert result["success"] is True
            content = result.get("content", "")
            assert any(hashtag in content for hashtag in brand_guidelines["hashtags"])
    
    @pytest.mark.integration
    async def test_scheduling_coordination(self, coordination_system, platform_agents):
        """Test coordinated scheduling across platforms."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Schedule posts for different times
        schedule = {
            "facebook": datetime.utcnow() + timedelta(minutes=5),
            "twitter": datetime.utcnow() + timedelta(minutes=10),
            "instagram": datetime.utcnow() + timedelta(minutes=15),
            "linkedin": datetime.utcnow() + timedelta(minutes=20),
            "tiktok": datetime.utcnow() + timedelta(minutes=25)
        }
        
        scheduling_results = await coordination_system.schedule_coordinated_posts(
            "Scheduled content test",
            schedule
        )
        
        # Verify scheduling
        assert len(scheduling_results) == 5
        for platform, result in scheduling_results.items():
            assert result["scheduled"] is True
            assert "scheduled_time" in result
    
    @pytest.mark.integration
    async def test_performance_monitoring(self, coordination_system, platform_agents):
        """Test performance monitoring and optimization."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Run performance monitoring
        performance_report = await coordination_system.monitor_performance()
        
        assert "agent_performance" in performance_report
        assert "system_performance" in performance_report
        assert "recommendations" in performance_report
        
        # Verify performance metrics
        for platform in ["facebook", "twitter", "instagram", "linkedin", "tiktok"]:
            assert platform in performance_report["agent_performance"]
    
    @pytest.mark.integration
    async def test_team_leader_reporting(self, team_leader, coordination_system):
        """Test team leader weekly reporting functionality."""
        # Generate weekly report
        report = await team_leader.generate_weekly_report()
        
        assert "summary" in report
        assert "platform_performance" in report
        assert "recommendations" in report
        assert "generated_at" in report
        
        # Verify report structure
        assert isinstance(report["platform_performance"], dict)
        assert isinstance(report["recommendations"], list)
    
    @pytest.mark.integration
    async def test_agent_communication(self, coordination_system, platform_agents):
        """Test inter-agent communication and coordination."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Test message broadcasting
        message = {
            "type": "content_update",
            "data": {"new_hashtag": "#trending"},
            "sender": "team_leader"
        }
        
        broadcast_results = await coordination_system.broadcast_message(message)
        
        # Verify message delivery
        assert len(broadcast_results) == 5
        for platform, result in broadcast_results.items():
            assert result["delivered"] is True
    
    @pytest.mark.integration
    async def test_failover_mechanisms(self, coordination_system, platform_agents):
        """Test failover mechanisms when agents fail."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Simulate multiple agent failures
        platform_agents["facebook"].is_running = False
        platform_agents["twitter"].is_running = False
        
        # Test system resilience
        health_check = await coordination_system.check_system_health()
        
        assert health_check["operational_agents"] == 3
        assert health_check["failed_agents"] == 2
        assert health_check["system_status"] == "degraded"
    
    @pytest.mark.integration
    async def test_content_approval_workflow(self, coordination_system, platform_agents):
        """Test content approval workflow."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Create content requiring approval
        content_draft = {
            "content": "Important company announcement",
            "platforms": ["facebook", "twitter", "linkedin"],
            "requires_approval": True
        }
        
        # Submit for approval
        approval_request = await coordination_system.submit_for_approval(content_draft)
        
        assert approval_request["status"] == "pending_approval"
        assert "approval_id" in approval_request
        
        # Simulate approval
        approval_result = await coordination_system.approve_content(
            approval_request["approval_id"],
            approved=True
        )
        
        assert approval_result["approved"] is True
        assert "scheduled_posts" in approval_result
    
    @pytest.mark.integration
    async def test_analytics_aggregation(self, coordination_system, platform_agents):
        """Test analytics aggregation across platforms."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Collect and aggregate analytics
        analytics_report = await coordination_system.aggregate_analytics()
        
        assert "total_engagement" in analytics_report
        assert "platform_breakdown" in analytics_report
        assert "trending_content" in analytics_report
        assert "performance_insights" in analytics_report
        
        # Verify analytics structure
        assert len(analytics_report["platform_breakdown"]) == 5
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_long_running_coordination(self, coordination_system, platform_agents):
        """Test long-running coordination scenarios."""
        # Start agents
        await coordination_system.start_all_agents()
        
        # Simulate long-running operation
        start_time = datetime.utcnow()
        
        # Run coordination for extended period (simulated)
        for i in range(5):
            await coordination_system.create_coordinated_post(f"Long running test {i}")
            await asyncio.sleep(0.1)  # Simulate time passage
        
        end_time = datetime.utcnow()
        
        # Verify system stability
        health_check = await coordination_system.check_system_health()
        assert health_check["system_status"] in ["healthy", "operational"]
        
        # Verify all agents still responsive
        for agent in platform_agents.values():
            assert agent.is_running is True


class TestTeamLeaderIntegration:
    """Integration tests specifically for Team Leader functionality."""
    
    @pytest.mark.integration
    async def test_team_leader_initialization(self, team_leader):
        """Test team leader initialization."""
        assert team_leader.name == "team_leader"
        assert team_leader.agents == {}
        assert team_leader.coordination_system is not None
    
    @pytest.mark.integration
    async def test_agent_registration(self, team_leader, platform_agents):
        """Test agent registration with team leader."""
        for platform, agent in platform_agents.items():
            team_leader.register_agent(agent)
        
        assert len(team_leader.agents) == 5
        
        for platform in ["facebook", "twitter", "instagram", "linkedin", "tiktok"]:
            assert platform in team_leader.agents
    
    @pytest.mark.integration
    async def test_weekly_report_generation(self, team_leader, platform_agents):
        """Test comprehensive weekly report generation."""
        # Register agents
        for platform, agent in platform_agents.items():
            team_leader.register_agent(agent)
        
        # Generate report
        report = await team_leader.generate_weekly_report()
        
        # Verify report completeness
        required_sections = [
            "summary",
            "platform_performance",
            "top_content",
            "growth_metrics",
            "engagement_insights",
            "recommendations"
        ]
        
        for section in required_sections:
            assert section in report
    
    @pytest.mark.integration
    async def test_strategic_planning(self, team_leader, platform_agents):
        """Test strategic planning functionality."""
        # Register agents
        for platform, agent in platform_agents.items():
            team_leader.register_agent(agent)
        
        # Create strategic plan
        strategy = await team_leader.create_content_strategy(
            theme="digital_transformation",
            duration_days=7,
            target_metrics={"engagement_rate": 5.0, "reach": 10000}
        )
        
        assert "content_calendar" in strategy
        assert "platform_assignments" in strategy
        assert "success_metrics" in strategy
        assert "timeline" in strategy

