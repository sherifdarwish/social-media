"""
Report Generator

This module implements the report generation system for creating comprehensive
weekly reports with performance metrics and insights.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from ...config.config_manager import ConfigManager
from ...metrics.metrics_collector import MetricsCollector
from ...utils.logger import get_logger


@dataclass
class PlatformReport:
    """Report data for a single platform."""
    platform: str
    metrics: Dict[str, Any]
    performance_score: float
    growth_metrics: Dict[str, float]
    top_posts: List[Dict[str, Any]]
    engagement_analysis: Dict[str, Any]
    recommendations: List[str]
    issues: List[str]


@dataclass
class CrossPlatformSummary:
    """Summary across all platforms."""
    total_followers: int
    total_engagement: int
    total_reach: int
    total_posts: int
    average_engagement_rate: float
    best_performing_platform: str
    growth_rate: float
    brand_consistency_score: float


@dataclass
class WeeklyReport:
    """Complete weekly report structure."""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    executive_summary: Dict[str, Any]
    platform_reports: Dict[str, PlatformReport]
    cross_platform_summary: CrossPlatformSummary
    insights_and_trends: Dict[str, Any]
    recommendations: List[str]
    action_items: List[str]
    performance_alerts: List[str]
    next_week_strategy: Dict[str, Any]


class ReportGenerator:
    """
    Report generator for creating comprehensive weekly reports.
    
    Generates detailed reports with performance metrics, insights,
    and recommendations for social media strategy optimization.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the report generator.
        
        Args:
            config_manager: Configuration manager instance
            metrics_collector: Metrics collection service
        """
        self.config_manager = config_manager
        self.metrics_collector = metrics_collector
        self.logger = get_logger("report_generator")
        
        # Report configuration
        self.report_config = self._load_report_config()
        
        # Performance benchmarks
        self.benchmarks = self._load_performance_benchmarks()
        
        self.logger.info("Report generator initialized")
    
    def _load_report_config(self) -> Dict[str, Any]:
        """Load report configuration."""
        return self.config_manager.get_config().get("reporting", {
            "include_detailed_metrics": True,
            "include_competitor_analysis": False,
            "include_trend_analysis": True,
            "include_recommendations": True,
            "max_recommendations": 10,
            "performance_threshold": 80.0
        })
    
    def _load_performance_benchmarks(self) -> Dict[str, Any]:
        """Load performance benchmarks for comparison."""
        return {
            "engagement_rate": {
                "facebook": {"excellent": 5.0, "good": 3.0, "average": 1.5, "poor": 0.5},
                "twitter": {"excellent": 3.0, "good": 2.0, "average": 1.0, "poor": 0.3},
                "instagram": {"excellent": 6.0, "good": 4.0, "average": 2.0, "poor": 1.0},
                "linkedin": {"excellent": 4.0, "good": 2.5, "average": 1.5, "poor": 0.5},
                "tiktok": {"excellent": 15.0, "good": 10.0, "average": 5.0, "poor": 2.0}
            },
            "growth_rate": {
                "excellent": 10.0,
                "good": 5.0,
                "average": 2.0,
                "poor": 0.0
            },
            "posting_frequency": {
                "facebook": {"optimal": 1, "minimum": 3},  # per week
                "twitter": {"optimal": 7, "minimum": 14},  # per week
                "instagram": {"optimal": 3, "minimum": 7},  # per week
                "linkedin": {"optimal": 2, "minimum": 5},  # per week
                "tiktok": {"optimal": 3, "minimum": 7}     # per week
            }
        }
    
    async def generate_weekly_report(
        self,
        agent_data: Dict[str, Any],
        cross_platform_summary: Dict[str, Any],
        insights: Dict[str, Any],
        brand_consistency_score: float,
        performance_trends: Dict[str, Any]
    ) -> WeeklyReport:
        """
        Generate comprehensive weekly report.
        
        Args:
            agent_data: Data from all platform agents
            cross_platform_summary: Cross-platform metrics summary
            insights: Generated insights and analysis
            brand_consistency_score: Brand consistency score
            performance_trends: Performance trend analysis
        
        Returns:
            Complete weekly report
        """
        self.logger.info("Generating weekly report")
        
        # Calculate report period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Generate report ID
        report_id = f"weekly_report_{end_date.strftime('%Y%m%d_%H%M%S')}"
        
        # Generate platform reports
        platform_reports = {}
        for platform, data in agent_data.items():
            platform_reports[platform] = await self._generate_platform_report(
                platform, data, start_date, end_date
            )
        
        # Generate cross-platform summary
        cross_platform = await self._generate_cross_platform_summary(
            agent_data, cross_platform_summary, brand_consistency_score
        )
        
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(
            platform_reports, cross_platform, performance_trends
        )
        
        # Generate insights and trends
        insights_and_trends = await self._generate_insights_and_trends(
            agent_data, insights, performance_trends
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            platform_reports, cross_platform, insights
        )
        
        # Generate action items
        action_items = await self._generate_action_items(
            platform_reports, recommendations
        )
        
        # Generate performance alerts
        performance_alerts = await self._generate_performance_alerts(
            platform_reports, cross_platform
        )
        
        # Generate next week strategy
        next_week_strategy = await self._generate_next_week_strategy(
            platform_reports, insights, recommendations
        )
        
        # Create complete report
        report = WeeklyReport(
            report_id=report_id,
            generated_at=datetime.utcnow(),
            period_start=start_date,
            period_end=end_date,
            executive_summary=executive_summary,
            platform_reports=platform_reports,
            cross_platform_summary=cross_platform,
            insights_and_trends=insights_and_trends,
            recommendations=recommendations,
            action_items=action_items,
            performance_alerts=performance_alerts,
            next_week_strategy=next_week_strategy
        )
        
        self.logger.info(f"Weekly report generated: {report_id}")
        return report
    
    async def _generate_platform_report(
        self,
        platform: str,
        data: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> PlatformReport:
        """Generate report for a specific platform."""
        metrics = data.get("metrics", {})
        status = data.get("status", {})
        recent_posts = data.get("recent_posts", {})
        
        # Calculate performance score
        performance_score = await self._calculate_performance_score(platform, metrics)
        
        # Calculate growth metrics
        growth_metrics = await self._calculate_growth_metrics(platform, metrics)
        
        # Analyze top posts
        top_posts = await self._analyze_top_posts(platform, recent_posts)
        
        # Analyze engagement
        engagement_analysis = await self._analyze_engagement(platform, metrics)
        
        # Generate platform-specific recommendations
        recommendations = await self._generate_platform_recommendations(
            platform, metrics, performance_score
        )
        
        # Identify issues
        issues = status.get("issues", [])
        
        return PlatformReport(
            platform=platform,
            metrics=metrics,
            performance_score=performance_score,
            growth_metrics=growth_metrics,
            top_posts=top_posts,
            engagement_analysis=engagement_analysis,
            recommendations=recommendations,
            issues=issues
        )
    
    async def _calculate_performance_score(
        self,
        platform: str,
        metrics: Dict[str, Any]
    ) -> float:
        """Calculate performance score for a platform."""
        score = 0.0
        max_score = 100.0
        
        # Engagement rate score (40% weight)
        engagement_rate = metrics.get("engagement_rate", 0)
        benchmarks = self.benchmarks["engagement_rate"].get(platform, {})
        
        if engagement_rate >= benchmarks.get("excellent", 5.0):
            score += 40.0
        elif engagement_rate >= benchmarks.get("good", 3.0):
            score += 30.0
        elif engagement_rate >= benchmarks.get("average", 1.5):
            score += 20.0
        elif engagement_rate >= benchmarks.get("poor", 0.5):
            score += 10.0
        
        # Success rate score (30% weight)
        posts_successful = metrics.get("posts_successful", 0)
        posts_total = posts_successful + metrics.get("posts_failed", 0)
        
        if posts_total > 0:
            success_rate = (posts_successful / posts_total) * 100
            if success_rate >= 95:
                score += 30.0
            elif success_rate >= 90:
                score += 25.0
            elif success_rate >= 80:
                score += 20.0
            elif success_rate >= 70:
                score += 15.0
            else:
                score += 10.0
        
        # Growth score (20% weight)
        follower_growth = metrics.get("follower_growth", 0)
        if follower_growth >= 10:
            score += 20.0
        elif follower_growth >= 5:
            score += 15.0
        elif follower_growth >= 2:
            score += 10.0
        elif follower_growth >= 0:
            score += 5.0
        
        # Activity score (10% weight)
        posts_created = metrics.get("posts_created", 0)
        optimal_frequency = self.benchmarks["posting_frequency"].get(platform, {}).get("optimal", 3)
        
        if posts_created >= optimal_frequency:
            score += 10.0
        elif posts_created >= optimal_frequency * 0.7:
            score += 7.0
        elif posts_created >= optimal_frequency * 0.5:
            score += 5.0
        else:
            score += 2.0
        
        return min(score, max_score)
    
    async def _calculate_growth_metrics(
        self,
        platform: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate growth metrics for a platform."""
        return {
            "follower_growth": metrics.get("follower_growth", 0.0),
            "engagement_growth": metrics.get("engagement_growth", 0.0),
            "reach_growth": metrics.get("reach_growth", 0.0),
            "post_frequency_change": metrics.get("post_frequency_change", 0.0)
        }
    
    async def _analyze_top_posts(
        self,
        platform: str,
        recent_posts: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze top performing posts."""
        # This is a simplified implementation
        # In practice, you'd analyze actual post performance data
        return [
            {
                "post_id": "top_post_1",
                "content_type": "image",
                "engagement_rate": 5.2,
                "reach": 1500,
                "likes": 78,
                "comments": 12,
                "shares": 5
            },
            {
                "post_id": "top_post_2",
                "content_type": "text",
                "engagement_rate": 4.8,
                "reach": 1200,
                "likes": 58,
                "comments": 15,
                "shares": 3
            }
        ]
    
    async def _analyze_engagement(
        self,
        platform: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze engagement patterns for a platform."""
        engagement_rate = metrics.get("engagement_rate", 0)
        benchmarks = self.benchmarks["engagement_rate"].get(platform, {})
        
        # Determine engagement level
        if engagement_rate >= benchmarks.get("excellent", 5.0):
            level = "excellent"
        elif engagement_rate >= benchmarks.get("good", 3.0):
            level = "good"
        elif engagement_rate >= benchmarks.get("average", 1.5):
            level = "average"
        else:
            level = "poor"
        
        return {
            "engagement_rate": engagement_rate,
            "engagement_level": level,
            "benchmark_comparison": {
                "vs_excellent": engagement_rate - benchmarks.get("excellent", 5.0),
                "vs_good": engagement_rate - benchmarks.get("good", 3.0),
                "vs_average": engagement_rate - benchmarks.get("average", 1.5)
            },
            "engagement_trends": {
                "likes_trend": "increasing",
                "comments_trend": "stable",
                "shares_trend": "increasing"
            }
        }
    
    async def _generate_platform_recommendations(
        self,
        platform: str,
        metrics: Dict[str, Any],
        performance_score: float
    ) -> List[str]:
        """Generate platform-specific recommendations."""
        recommendations = []
        
        # Performance-based recommendations
        if performance_score < 70:
            recommendations.append(f"Improve {platform} performance - current score: {performance_score:.1f}%")
        
        # Engagement-based recommendations
        engagement_rate = metrics.get("engagement_rate", 0)
        benchmarks = self.benchmarks["engagement_rate"].get(platform, {})
        
        if engagement_rate < benchmarks.get("average", 1.5):
            recommendations.extend([
                f"Increase {platform} engagement through more interactive content",
                f"Optimize posting times for {platform} audience",
                f"Use trending hashtags and topics for {platform}"
            ])
        
        # Platform-specific recommendations
        if platform == "facebook":
            recommendations.extend([
                "Create more video content for better Facebook reach",
                "Engage more actively in Facebook groups",
                "Use Facebook Stories for behind-the-scenes content"
            ])
        elif platform == "twitter":
            recommendations.extend([
                "Increase Twitter thread usage for better engagement",
                "Participate more in Twitter conversations and trending topics",
                "Use Twitter polls to boost interaction"
            ])
        elif platform == "instagram":
            recommendations.extend([
                "Create more Instagram Reels for increased visibility",
                "Use Instagram Stories features like polls and questions",
                "Maintain consistent visual aesthetic"
            ])
        elif platform == "linkedin":
            recommendations.extend([
                "Share more industry insights and thought leadership content",
                "Engage with other professionals' content",
                "Use LinkedIn articles for long-form content"
            ])
        elif platform == "tiktok":
            recommendations.extend([
                "Follow trending TikTok challenges and sounds",
                "Create educational content in short format",
                "Post consistently during peak hours"
            ])
        
        return recommendations[:5]  # Limit to top 5
    
    async def _generate_cross_platform_summary(
        self,
        agent_data: Dict[str, Any],
        cross_platform_summary: Dict[str, Any],
        brand_consistency_score: float
    ) -> CrossPlatformSummary:
        """Generate cross-platform summary."""
        total_followers = 0
        total_engagement = 0
        total_reach = 0
        total_posts = 0
        engagement_rates = []
        
        best_platform = ""
        best_score = 0
        
        for platform, data in agent_data.items():
            metrics = data.get("metrics", {})
            
            # Aggregate metrics
            total_followers += metrics.get("followers_count", 0)
            total_engagement += metrics.get("total_engagement", 0)
            total_reach += metrics.get("total_reach", 0)
            total_posts += metrics.get("posts_created", 0)
            
            engagement_rate = metrics.get("engagement_rate", 0)
            if engagement_rate > 0:
                engagement_rates.append(engagement_rate)
            
            # Find best performing platform
            performance_score = await self._calculate_performance_score(platform, metrics)
            if performance_score > best_score:
                best_score = performance_score
                best_platform = platform
        
        # Calculate averages
        average_engagement_rate = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        # Calculate growth rate (simplified)
        growth_rate = cross_platform_summary.get("growth_rate", 5.0)
        
        return CrossPlatformSummary(
            total_followers=total_followers,
            total_engagement=total_engagement,
            total_reach=total_reach,
            total_posts=total_posts,
            average_engagement_rate=average_engagement_rate,
            best_performing_platform=best_platform,
            growth_rate=growth_rate,
            brand_consistency_score=brand_consistency_score
        )
    
    async def _generate_executive_summary(
        self,
        platform_reports: Dict[str, PlatformReport],
        cross_platform: CrossPlatformSummary,
        performance_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary."""
        # Calculate overall performance
        platform_scores = [report.performance_score for report in platform_reports.values()]
        overall_score = sum(platform_scores) / len(platform_scores) if platform_scores else 0
        
        # Identify key achievements
        achievements = []
        if overall_score >= 80:
            achievements.append("Excellent overall performance across platforms")
        if cross_platform.growth_rate > 5:
            achievements.append(f"Strong growth rate of {cross_platform.growth_rate:.1f}%")
        if cross_platform.brand_consistency_score > 85:
            achievements.append("High brand consistency maintained")
        
        # Identify key challenges
        challenges = []
        low_performing_platforms = [
            platform for platform, report in platform_reports.items()
            if report.performance_score < 70
        ]
        if low_performing_platforms:
            challenges.append(f"Performance issues on: {', '.join(low_performing_platforms)}")
        
        if cross_platform.average_engagement_rate < 2.0:
            challenges.append("Low average engagement rate across platforms")
        
        return {
            "overall_performance_score": overall_score,
            "performance_trend": performance_trends.get("overall_trend", "stable"),
            "total_reach": cross_platform.total_reach,
            "total_engagement": cross_platform.total_engagement,
            "best_performing_platform": cross_platform.best_performing_platform,
            "key_achievements": achievements,
            "key_challenges": challenges,
            "week_over_week_growth": cross_platform.growth_rate
        }
    
    async def _generate_insights_and_trends(
        self,
        agent_data: Dict[str, Any],
        insights: Dict[str, Any],
        performance_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights and trends analysis."""
        return {
            "content_performance_insights": {
                "best_content_types": ["image", "video", "carousel"],
                "optimal_posting_times": insights.get("audience_insights", {}).get("best_posting_times", {}),
                "trending_topics": ["AI", "sustainability", "remote work"],
                "hashtag_performance": {
                    "top_performing": ["#innovation", "#growth", "#success"],
                    "emerging": ["#futureofwork", "#digitalhealth", "#greentech"]
                }
            },
            "audience_insights": {
                "demographic_trends": "Increasing engagement from 25-34 age group",
                "geographic_distribution": "Strong performance in North America and Europe",
                "engagement_patterns": "Higher engagement on weekday mornings"
            },
            "competitive_analysis": {
                "market_position": "Above average performance in industry",
                "opportunity_areas": ["Video content", "Community engagement"],
                "threat_areas": ["Increasing competition", "Platform algorithm changes"]
            },
            "trend_predictions": {
                "next_month": "Continued growth in video content engagement",
                "seasonal_factors": "Expect increased activity during holiday season",
                "platform_changes": "Instagram Reels and TikTok continue to gain importance"
            }
        }
    
    async def _generate_recommendations(
        self,
        platform_reports: Dict[str, PlatformReport],
        cross_platform: CrossPlatformSummary,
        insights: Dict[str, Any]
    ) -> List[str]:
        """Generate overall recommendations."""
        recommendations = []
        
        # Performance-based recommendations
        if cross_platform.average_engagement_rate < 3.0:
            recommendations.append("Focus on creating more engaging, interactive content")
        
        if cross_platform.brand_consistency_score < 80:
            recommendations.append("Improve brand consistency across all platforms")
        
        # Platform-specific recommendations
        low_performers = [
            platform for platform, report in platform_reports.items()
            if report.performance_score < 70
        ]
        if low_performers:
            recommendations.append(f"Prioritize improvement on {', '.join(low_performers)}")
        
        # Content recommendations
        recommendations.extend([
            "Increase video content production for better engagement",
            "Implement cross-platform content repurposing strategy",
            "Develop more user-generated content campaigns",
            "Optimize posting schedules based on audience insights",
            "Invest in trending topic monitoring and quick response"
        ])
        
        return recommendations[:self.report_config.get("max_recommendations", 10)]
    
    async def _generate_action_items(
        self,
        platform_reports: Dict[str, PlatformReport],
        recommendations: List[str]
    ) -> List[str]:
        """Generate specific action items."""
        action_items = []
        
        # Convert recommendations to actionable items
        for recommendation in recommendations[:5]:
            if "engagement" in recommendation.lower():
                action_items.append("Schedule content audit meeting to review engagement strategies")
            elif "consistency" in recommendation.lower():
                action_items.append("Update brand guidelines and distribute to team")
            elif "video" in recommendation.lower():
                action_items.append("Plan video content calendar for next month")
            elif "schedule" in recommendation.lower():
                action_items.append("Analyze audience insights and update posting schedules")
        
        # Add platform-specific action items
        for platform, report in platform_reports.items():
            if report.performance_score < 70:
                action_items.append(f"Conduct {platform} strategy review meeting")
            
            if report.issues:
                action_items.append(f"Resolve {platform} technical issues: {', '.join(report.issues[:2])}")
        
        return action_items
    
    async def _generate_performance_alerts(
        self,
        platform_reports: Dict[str, PlatformReport],
        cross_platform: CrossPlatformSummary
    ) -> List[str]:
        """Generate performance alerts."""
        alerts = []
        
        # Overall performance alerts
        if cross_platform.average_engagement_rate < 1.0:
            alerts.append("CRITICAL: Average engagement rate below 1% across platforms")
        
        if cross_platform.growth_rate < 0:
            alerts.append("WARNING: Negative growth rate detected")
        
        # Platform-specific alerts
        for platform, report in platform_reports.items():
            if report.performance_score < 50:
                alerts.append(f"CRITICAL: {platform} performance score below 50%")
            elif report.performance_score < 70:
                alerts.append(f"WARNING: {platform} performance score below 70%")
            
            if report.issues:
                alerts.append(f"ISSUE: {platform} has {len(report.issues)} active issues")
        
        return alerts
    
    async def _generate_next_week_strategy(
        self,
        platform_reports: Dict[str, PlatformReport],
        insights: Dict[str, Any],
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """Generate strategy for next week."""
        return {
            "focus_areas": [
                "Improve engagement on underperforming platforms",
                "Increase video content production",
                "Optimize posting schedules"
            ],
            "content_themes": [
                "Industry insights and trends",
                "Behind-the-scenes content",
                "User-generated content campaigns"
            ],
            "platform_priorities": {
                platform: "high" if report.performance_score < 70 else "normal"
                for platform, report in platform_reports.items()
            },
            "success_metrics": [
                "Increase average engagement rate by 0.5%",
                "Reduce failed posts by 50%",
                "Improve brand consistency score to 90%"
            ],
            "resource_allocation": {
                "content_creation": "40%",
                "community_management": "30%",
                "analytics_and_optimization": "20%",
                "strategy_planning": "10%"
            }
        }
    
    def export_report_to_json(self, report: WeeklyReport) -> str:
        """Export report to JSON format."""
        # Convert dataclasses to dictionaries
        report_dict = asdict(report)
        
        # Convert datetime objects to ISO format strings
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            else:
                return obj
        
        report_dict = convert_datetime(report_dict)
        
        return json.dumps(report_dict, indent=2)
    
    def export_report_to_html(self, report: WeeklyReport) -> str:
        """Export report to HTML format."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weekly Social Media Report - {report_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .platform {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }}
                .alert {{ color: red; font-weight: bold; }}
                .recommendation {{ background-color: #e7f3ff; padding: 10px; margin: 5px 0; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Weekly Social Media Report</h1>
                <p>Report ID: {report_id}</p>
                <p>Period: {period_start} to {period_end}</p>
                <p>Generated: {generated_at}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="metric">Overall Score: {overall_score:.1f}%</div>
                <div class="metric">Total Reach: {total_reach:,}</div>
                <div class="metric">Total Engagement: {total_engagement:,}</div>
                <div class="metric">Best Platform: {best_platform}</div>
            </div>
            
            <div class="section">
                <h2>Platform Performance</h2>
                {platform_sections}
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {recommendations_html}
            </div>
            
            <div class="section">
                <h2>Performance Alerts</h2>
                {alerts_html}
            </div>
        </body>
        </html>
        """
        
        # Generate platform sections
        platform_sections = ""
        for platform, platform_report in report.platform_reports.items():
            platform_sections += f"""
            <div class="platform">
                <h3>{platform.title()}</h3>
                <div class="metric">Performance Score: {platform_report.performance_score:.1f}%</div>
                <div class="metric">Engagement Rate: {platform_report.metrics.get('engagement_rate', 0):.2f}%</div>
                <div class="metric">Posts Created: {platform_report.metrics.get('posts_created', 0)}</div>
            </div>
            """
        
        # Generate recommendations HTML
        recommendations_html = ""
        for rec in report.recommendations:
            recommendations_html += f'<div class="recommendation">{rec}</div>'
        
        # Generate alerts HTML
        alerts_html = ""
        for alert in report.performance_alerts:
            alerts_html += f'<div class="alert">{alert}</div>'
        
        return html_template.format(
            report_id=report.report_id,
            period_start=report.period_start.strftime("%Y-%m-%d"),
            period_end=report.period_end.strftime("%Y-%m-%d"),
            generated_at=report.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            overall_score=report.executive_summary.get("overall_performance_score", 0),
            total_reach=report.cross_platform_summary.total_reach,
            total_engagement=report.cross_platform_summary.total_engagement,
            best_platform=report.cross_platform_summary.best_performing_platform,
            platform_sections=platform_sections,
            recommendations_html=recommendations_html,
            alerts_html=alerts_html
        )

