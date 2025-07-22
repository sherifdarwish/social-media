"""
Report Generator

This module generates comprehensive reports for social media performance,
including weekly progress reports, analytics dashboards, and insights.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path
import base64
import io

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

from .metrics_collector import MetricsCollector, MetricSnapshot
from ..utils.logger import get_logger


class ReportType(Enum):
    """Types of reports that can be generated."""
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_OVERVIEW = "monthly_overview"
    PLATFORM_COMPARISON = "platform_comparison"
    CONTENT_PERFORMANCE = "content_performance"
    ENGAGEMENT_ANALYSIS = "engagement_analysis"
    GROWTH_TRACKING = "growth_tracking"
    CUSTOM_DASHBOARD = "custom_dashboard"


class ReportFormat(Enum):
    """Output formats for reports."""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    MARKDOWN = "markdown"
    EXCEL = "excel"


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    report_type: ReportType
    format: ReportFormat
    include_charts: bool = True
    include_recommendations: bool = True
    include_raw_data: bool = False
    chart_style: str = "seaborn"
    color_scheme: str = "viridis"
    custom_branding: bool = False
    logo_path: Optional[str] = None


@dataclass
class ReportSection:
    """Individual section of a report."""
    title: str
    content: str
    charts: List[str] = None
    data: Dict[str, Any] = None
    insights: List[str] = None
    
    def __post_init__(self):
        if self.charts is None:
            self.charts = []
        if self.data is None:
            self.data = {}
        if self.insights is None:
            self.insights = []


@dataclass
class WeeklyReport:
    """Weekly progress report structure."""
    week_start: datetime
    week_end: datetime
    generated_at: datetime
    summary: Dict[str, Any]
    platform_performance: Dict[str, Dict[str, Any]]
    top_content: List[Dict[str, Any]]
    growth_metrics: Dict[str, Any]
    engagement_insights: Dict[str, Any]
    recommendations: List[str]
    charts: Dict[str, str]  # Chart name -> base64 encoded image
    raw_data: Optional[Dict[str, Any]] = None


class ReportGenerator:
    """
    Comprehensive report generator for social media analytics.
    
    Generates various types of reports including weekly summaries,
    performance analytics, and custom dashboards with visualizations.
    """
    
    def __init__(self, metrics_collector: MetricsCollector, config: Optional[ReportConfig] = None):
        """
        Initialize the report generator.
        
        Args:
            metrics_collector: Metrics collector instance
            config: Report configuration
        """
        self.metrics_collector = metrics_collector
        self.config = config or ReportConfig(
            report_type=ReportType.WEEKLY_SUMMARY,
            format=ReportFormat.HTML
        )
        self.logger = get_logger("report_generator")
        
        # Setup plotting style
        self._setup_plotting_style()
        
        # Report templates
        self.templates = self._load_report_templates()
        
        # Chart configurations
        self.chart_configs = self._setup_chart_configs()
        
        self.logger.info("Report generator initialized")
    
    def _setup_plotting_style(self):
        """Setup matplotlib and seaborn styling."""
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette(self.config.color_scheme)
        
        # Set default figure parameters
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
    
    def _load_report_templates(self) -> Dict[str, str]:
        """Load HTML templates for reports."""
        return {
            "weekly_summary": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Weekly Social Media Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .section { margin-bottom: 30px; }
                    .metric-card { 
                        display: inline-block; 
                        background: #f5f5f5; 
                        padding: 20px; 
                        margin: 10px; 
                        border-radius: 8px; 
                        min-width: 200px;
                    }
                    .chart-container { text-align: center; margin: 20px 0; }
                    .recommendations { background: #e8f4fd; padding: 20px; border-radius: 8px; }
                    .platform-section { border-left: 4px solid #007acc; padding-left: 20px; margin: 20px 0; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                {content}
            </body>
            </html>
            """,
            
            "platform_comparison": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Platform Comparison Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .comparison-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                    .platform-card { background: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd; }
                    .metric-value { font-size: 24px; font-weight: bold; color: #007acc; }
                    .metric-label { font-size: 14px; color: #666; }
                    .chart-container { text-align: center; margin: 20px 0; }
                </style>
            </head>
            <body>
                {content}
            </body>
            </html>
            """
        }
    
    def _setup_chart_configs(self) -> Dict[str, Dict[str, Any]]:
        """Setup chart configurations."""
        return {
            "engagement_trend": {
                "type": "line",
                "title": "Engagement Trend Over Time",
                "x_label": "Date",
                "y_label": "Engagement Rate (%)",
                "color": "#007acc"
            },
            "platform_comparison": {
                "type": "bar",
                "title": "Platform Performance Comparison",
                "x_label": "Platform",
                "y_label": "Total Engagement",
                "color_palette": "viridis"
            },
            "content_performance": {
                "type": "scatter",
                "title": "Content Performance Analysis",
                "x_label": "Reach",
                "y_label": "Engagement Rate",
                "size_column": "impressions"
            },
            "growth_metrics": {
                "type": "area",
                "title": "Follower Growth Over Time",
                "x_label": "Date",
                "y_label": "Followers",
                "fill_alpha": 0.3
            }
        }
    
    async def generate_weekly_report(
        self,
        week_start: Optional[datetime] = None,
        week_end: Optional[datetime] = None,
        platforms: Optional[List[str]] = None
    ) -> WeeklyReport:
        """
        Generate comprehensive weekly report.
        
        Args:
            week_start: Start of the week (default: last Monday)
            week_end: End of the week (default: last Sunday)
            platforms: List of platforms to include
        
        Returns:
            WeeklyReport object
        """
        try:
            # Set default date range
            if week_end is None:
                week_end = datetime.utcnow()
            if week_start is None:
                week_start = week_end - timedelta(days=7)
            
            if platforms is None:
                platforms = ["facebook", "twitter", "instagram", "linkedin", "tiktok"]
            
            self.logger.info(f"Generating weekly report for {week_start.date()} to {week_end.date()}")
            
            # Collect data for all platforms
            platform_data = {}
            for platform in platforms:
                platform_data[platform] = await self._collect_platform_data(
                    platform, week_start, week_end
                )
            
            # Generate summary metrics
            summary = await self._generate_summary_metrics(platform_data, week_start, week_end)
            
            # Analyze platform performance
            platform_performance = await self._analyze_platform_performance(platform_data)
            
            # Identify top content
            top_content = await self._identify_top_content(platform_data)
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_growth_metrics(platform_data, week_start, week_end)
            
            # Generate engagement insights
            engagement_insights = await self._generate_engagement_insights(platform_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                platform_performance, growth_metrics, engagement_insights
            )
            
            # Create charts
            charts = await self._generate_weekly_charts(platform_data, week_start, week_end)
            
            # Create weekly report
            weekly_report = WeeklyReport(
                week_start=week_start,
                week_end=week_end,
                generated_at=datetime.utcnow(),
                summary=summary,
                platform_performance=platform_performance,
                top_content=top_content,
                growth_metrics=growth_metrics,
                engagement_insights=engagement_insights,
                recommendations=recommendations,
                charts=charts
            )
            
            self.logger.info("Weekly report generated successfully")
            return weekly_report
            
        except Exception as e:
            self.logger.error(f"Error generating weekly report: {e}")
            raise
    
    async def _collect_platform_data(
        self,
        platform: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Collect data for a specific platform."""
        try:
            # Get platform summary
            platform_summary = await self.metrics_collector.get_platform_summary(platform, "weekly")
            
            # Get agent metrics for the platform
            agent_metrics = await self.metrics_collector.get_agent_metrics(
                f"{platform}_agent", platform, start_time, end_time
            )
            
            # Calculate aggregated metrics
            total_engagement = sum(m.likes + m.comments + m.shares for m in agent_metrics)
            total_reach = sum(m.reach for m in agent_metrics)
            total_impressions = sum(m.impressions for m in agent_metrics)
            avg_engagement_rate = statistics.mean([m.engagement_rate for m in agent_metrics]) if agent_metrics else 0
            
            return {
                "platform": platform,
                "summary": platform_summary,
                "metrics": agent_metrics,
                "aggregated": {
                    "total_engagement": total_engagement,
                    "total_reach": total_reach,
                    "total_impressions": total_impressions,
                    "avg_engagement_rate": avg_engagement_rate,
                    "posts_count": len(agent_metrics),
                    "success_rate": platform_summary.get("success_rate", 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting data for platform {platform}: {e}")
            return {"platform": platform, "error": str(e)}
    
    async def _generate_summary_metrics(
        self,
        platform_data: Dict[str, Dict[str, Any]],
        week_start: datetime,
        week_end: datetime
    ) -> Dict[str, Any]:
        """Generate overall summary metrics."""
        try:
            total_posts = sum(
                data.get("aggregated", {}).get("posts_count", 0)
                for data in platform_data.values()
                if "error" not in data
            )
            
            total_engagement = sum(
                data.get("aggregated", {}).get("total_engagement", 0)
                for data in platform_data.values()
                if "error" not in data
            )
            
            total_reach = sum(
                data.get("aggregated", {}).get("total_reach", 0)
                for data in platform_data.values()
                if "error" not in data
            )
            
            total_impressions = sum(
                data.get("aggregated", {}).get("total_impressions", 0)
                for data in platform_data.values()
                if "error" not in data
            )
            
            engagement_rates = [
                data.get("aggregated", {}).get("avg_engagement_rate", 0)
                for data in platform_data.values()
                if "error" not in data and data.get("aggregated", {}).get("avg_engagement_rate", 0) > 0
            ]
            
            avg_engagement_rate = statistics.mean(engagement_rates) if engagement_rates else 0
            
            success_rates = [
                data.get("aggregated", {}).get("success_rate", 0)
                for data in platform_data.values()
                if "error" not in data
            ]
            
            overall_success_rate = statistics.mean(success_rates) if success_rates else 0
            
            return {
                "period": {
                    "start": week_start.isoformat(),
                    "end": week_end.isoformat(),
                    "days": (week_end - week_start).days
                },
                "totals": {
                    "posts": total_posts,
                    "engagement": total_engagement,
                    "reach": total_reach,
                    "impressions": total_impressions
                },
                "averages": {
                    "engagement_rate": round(avg_engagement_rate, 2),
                    "posts_per_day": round(total_posts / 7, 1),
                    "engagement_per_post": round(total_engagement / total_posts, 1) if total_posts > 0 else 0
                },
                "performance": {
                    "success_rate": round(overall_success_rate, 2),
                    "platforms_active": len([d for d in platform_data.values() if "error" not in d]),
                    "platforms_total": len(platform_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating summary metrics: {e}")
            return {"error": str(e)}
    
    async def _analyze_platform_performance(
        self,
        platform_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze performance for each platform."""
        try:
            performance_analysis = {}
            
            for platform, data in platform_data.items():
                if "error" in data:
                    performance_analysis[platform] = {"error": data["error"]}
                    continue
                
                aggregated = data.get("aggregated", {})
                metrics = data.get("metrics", [])
                
                # Calculate performance indicators
                engagement_trend = [m.engagement_rate for m in metrics[-7:]]  # Last 7 data points
                trend_direction = "stable"
                
                if len(engagement_trend) >= 2:
                    if engagement_trend[-1] > engagement_trend[0]:
                        trend_direction = "increasing"
                    elif engagement_trend[-1] < engagement_trend[0]:
                        trend_direction = "decreasing"
                
                # Performance rating
                engagement_rate = aggregated.get("avg_engagement_rate", 0)
                if engagement_rate >= 5:
                    performance_rating = "excellent"
                elif engagement_rate >= 3:
                    performance_rating = "good"
                elif engagement_rate >= 1:
                    performance_rating = "fair"
                else:
                    performance_rating = "needs_improvement"
                
                performance_analysis[platform] = {
                    "metrics": aggregated,
                    "trend": {
                        "direction": trend_direction,
                        "engagement_trend": engagement_trend
                    },
                    "rating": performance_rating,
                    "highlights": self._generate_platform_highlights(platform, aggregated, metrics),
                    "concerns": self._identify_platform_concerns(platform, aggregated, metrics)
                }
            
            return performance_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing platform performance: {e}")
            return {}
    
    def _generate_platform_highlights(
        self,
        platform: str,
        aggregated: Dict[str, Any],
        metrics: List[MetricSnapshot]
    ) -> List[str]:
        """Generate highlights for a platform."""
        highlights = []
        
        engagement_rate = aggregated.get("avg_engagement_rate", 0)
        success_rate = aggregated.get("success_rate", 0)
        posts_count = aggregated.get("posts_count", 0)
        
        if engagement_rate > 5:
            highlights.append(f"Excellent engagement rate of {engagement_rate:.1f}%")
        
        if success_rate > 95:
            highlights.append(f"High posting success rate of {success_rate:.1f}%")
        
        if posts_count > 10:
            highlights.append(f"Consistent posting with {posts_count} posts this week")
        
        # Check for growth in recent metrics
        if len(metrics) >= 2:
            recent_followers = metrics[-1].followers
            previous_followers = metrics[0].followers
            if recent_followers > previous_followers:
                growth = ((recent_followers - previous_followers) / previous_followers) * 100
                highlights.append(f"Follower growth of {growth:.1f}% this week")
        
        return highlights
    
    def _identify_platform_concerns(
        self,
        platform: str,
        aggregated: Dict[str, Any],
        metrics: List[MetricSnapshot]
    ) -> List[str]:
        """Identify concerns for a platform."""
        concerns = []
        
        engagement_rate = aggregated.get("avg_engagement_rate", 0)
        success_rate = aggregated.get("success_rate", 0)
        posts_count = aggregated.get("posts_count", 0)
        
        if engagement_rate < 1:
            concerns.append(f"Low engagement rate of {engagement_rate:.1f}%")
        
        if success_rate < 90:
            concerns.append(f"Posting failures detected ({success_rate:.1f}% success rate)")
        
        if posts_count < 3:
            concerns.append(f"Low posting frequency ({posts_count} posts this week)")
        
        # Check for declining trends
        if len(metrics) >= 3:
            recent_engagement = [m.engagement_rate for m in metrics[-3:]]
            if all(recent_engagement[i] > recent_engagement[i+1] for i in range(len(recent_engagement)-1)):
                concerns.append("Declining engagement trend detected")
        
        return concerns
    
    async def _identify_top_content(
        self,
        platform_data: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify top performing content across platforms."""
        try:
            all_content = []
            
            for platform, data in platform_data.items():
                if "error" in data:
                    continue
                
                metrics = data.get("metrics", [])
                for metric in metrics:
                    if metric.engagement_rate > 0:
                        all_content.append({
                            "platform": platform,
                            "timestamp": metric.timestamp,
                            "engagement_rate": metric.engagement_rate,
                            "total_engagement": metric.likes + metric.comments + metric.shares,
                            "reach": metric.reach,
                            "impressions": metric.impressions
                        })
            
            # Sort by engagement rate and return top 10
            top_content = sorted(all_content, key=lambda x: x["engagement_rate"], reverse=True)[:10]
            
            return top_content
            
        except Exception as e:
            self.logger.error(f"Error identifying top content: {e}")
            return []
    
    async def _calculate_growth_metrics(
        self,
        platform_data: Dict[str, Dict[str, Any]],
        week_start: datetime,
        week_end: datetime
    ) -> Dict[str, Any]:
        """Calculate growth metrics."""
        try:
            growth_metrics = {}
            
            for platform, data in platform_data.items():
                if "error" in data:
                    continue
                
                metrics = data.get("metrics", [])
                if len(metrics) < 2:
                    continue
                
                # Calculate follower growth
                start_followers = metrics[0].followers
                end_followers = metrics[-1].followers
                follower_growth = end_followers - start_followers
                follower_growth_rate = (follower_growth / start_followers * 100) if start_followers > 0 else 0
                
                # Calculate engagement growth
                start_engagement = metrics[0].likes + metrics[0].comments + metrics[0].shares
                end_engagement = metrics[-1].likes + metrics[-1].comments + metrics[-1].shares
                engagement_growth = end_engagement - start_engagement
                
                growth_metrics[platform] = {
                    "follower_growth": follower_growth,
                    "follower_growth_rate": round(follower_growth_rate, 2),
                    "engagement_growth": engagement_growth,
                    "current_followers": end_followers,
                    "posts_growth": len(metrics)
                }
            
            # Calculate overall growth
            total_follower_growth = sum(m.get("follower_growth", 0) for m in growth_metrics.values())
            total_engagement_growth = sum(m.get("engagement_growth", 0) for m in growth_metrics.values())
            
            growth_metrics["overall"] = {
                "total_follower_growth": total_follower_growth,
                "total_engagement_growth": total_engagement_growth,
                "platforms_growing": len([m for m in growth_metrics.values() if m.get("follower_growth", 0) > 0])
            }
            
            return growth_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating growth metrics: {e}")
            return {}
    
    async def _generate_engagement_insights(
        self,
        platform_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights about engagement patterns."""
        try:
            insights = {
                "best_performing_platform": None,
                "engagement_patterns": {},
                "content_insights": [],
                "timing_insights": []
            }
            
            # Find best performing platform
            platform_engagement = {}
            for platform, data in platform_data.items():
                if "error" not in data:
                    engagement_rate = data.get("aggregated", {}).get("avg_engagement_rate", 0)
                    platform_engagement[platform] = engagement_rate
            
            if platform_engagement:
                best_platform = max(platform_engagement, key=platform_engagement.get)
                insights["best_performing_platform"] = {
                    "platform": best_platform,
                    "engagement_rate": platform_engagement[best_platform]
                }
            
            # Analyze engagement patterns
            for platform, data in platform_data.items():
                if "error" in data:
                    continue
                
                metrics = data.get("metrics", [])
                if not metrics:
                    continue
                
                # Analyze posting times and engagement
                hourly_engagement = {}
                for metric in metrics:
                    hour = metric.timestamp.hour
                    if hour not in hourly_engagement:
                        hourly_engagement[hour] = []
                    hourly_engagement[hour].append(metric.engagement_rate)
                
                # Find best posting times
                avg_hourly_engagement = {
                    hour: statistics.mean(rates)
                    for hour, rates in hourly_engagement.items()
                    if rates
                }
                
                if avg_hourly_engagement:
                    best_hour = max(avg_hourly_engagement, key=avg_hourly_engagement.get)
                    insights["engagement_patterns"][platform] = {
                        "best_posting_hour": best_hour,
                        "best_engagement_rate": avg_hourly_engagement[best_hour],
                        "hourly_breakdown": avg_hourly_engagement
                    }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating engagement insights: {e}")
            return {}
    
    async def _generate_recommendations(
        self,
        platform_performance: Dict[str, Dict[str, Any]],
        growth_metrics: Dict[str, Any],
        engagement_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        try:
            recommendations = []
            
            # Platform-specific recommendations
            for platform, performance in platform_performance.items():
                if "error" in performance:
                    recommendations.append(f"Fix data collection issues for {platform}")
                    continue
                
                rating = performance.get("rating", "")
                concerns = performance.get("concerns", [])
                
                if rating == "needs_improvement":
                    recommendations.append(
                        f"Focus on improving {platform} content quality and engagement strategies"
                    )
                
                if concerns:
                    for concern in concerns[:2]:  # Limit to top 2 concerns
                        if "Low engagement" in concern:
                            recommendations.append(
                                f"Experiment with different content types and posting times on {platform}"
                            )
                        elif "Posting failures" in concern:
                            recommendations.append(
                                f"Review and fix posting automation issues on {platform}"
                            )
                        elif "Low posting frequency" in concern:
                            recommendations.append(
                                f"Increase posting frequency on {platform} to maintain audience engagement"
                            )
            
            # Growth-based recommendations
            overall_growth = growth_metrics.get("overall", {})
            if overall_growth.get("total_follower_growth", 0) < 0:
                recommendations.append(
                    "Implement follower retention strategies across all platforms"
                )
            
            # Engagement insights recommendations
            best_platform = engagement_insights.get("best_performing_platform")
            if best_platform:
                platform_name = best_platform["platform"]
                recommendations.append(
                    f"Apply successful strategies from {platform_name} to other platforms"
                )
            
            # Timing recommendations
            for platform, patterns in engagement_insights.get("engagement_patterns", {}).items():
                best_hour = patterns.get("best_posting_hour")
                if best_hour is not None:
                    recommendations.append(
                        f"Schedule more {platform} posts around {best_hour}:00 for better engagement"
                    )
            
            # General recommendations
            if len(recommendations) == 0:
                recommendations.append("Continue current strategy - performance is stable")
            
            # Limit to top 8 recommendations
            return recommendations[:8]
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Review system performance and data collection"]
    
    async def _generate_weekly_charts(
        self,
        platform_data: Dict[str, Dict[str, Any]],
        week_start: datetime,
        week_end: datetime
    ) -> Dict[str, str]:
        """Generate charts for the weekly report."""
        try:
            charts = {}
            
            # Engagement trend chart
            charts["engagement_trend"] = await self._create_engagement_trend_chart(platform_data)
            
            # Platform comparison chart
            charts["platform_comparison"] = await self._create_platform_comparison_chart(platform_data)
            
            # Growth metrics chart
            charts["growth_metrics"] = await self._create_growth_chart(platform_data)
            
            # Content performance chart
            charts["content_performance"] = await self._create_content_performance_chart(platform_data)
            
            return charts
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
            return {}
    
    async def _create_engagement_trend_chart(
        self,
        platform_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Create engagement trend chart."""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for platform, data in platform_data.items():
                if "error" in data:
                    continue
                
                metrics = data.get("metrics", [])
                if not metrics:
                    continue
                
                timestamps = [m.timestamp for m in metrics]
                engagement_rates = [m.engagement_rate for m in metrics]
                
                ax.plot(timestamps, engagement_rates, marker='o', label=platform.title(), linewidth=2)
            
            ax.set_title("Engagement Rate Trend", fontsize=16, fontweight='bold')
            ax.set_xlabel("Date")
            ax.set_ylabel("Engagement Rate (%)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_base64
            
        except Exception as e:
            self.logger.error(f"Error creating engagement trend chart: {e}")
            return ""
    
    async def _create_platform_comparison_chart(
        self,
        platform_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Create platform comparison chart."""
        try:
            platforms = []
            engagement_rates = []
            total_engagements = []
            
            for platform, data in platform_data.items():
                if "error" in data:
                    continue
                
                aggregated = data.get("aggregated", {})
                platforms.append(platform.title())
                engagement_rates.append(aggregated.get("avg_engagement_rate", 0))
                total_engagements.append(aggregated.get("total_engagement", 0))
            
            if not platforms:
                return ""
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Engagement rate comparison
            bars1 = ax1.bar(platforms, engagement_rates, color=sns.color_palette("viridis", len(platforms)))
            ax1.set_title("Average Engagement Rate by Platform", fontweight='bold')
            ax1.set_ylabel("Engagement Rate (%)")
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars1, engagement_rates):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{value:.1f}%', ha='center', va='bottom')
            
            # Total engagement comparison
            bars2 = ax2.bar(platforms, total_engagements, color=sns.color_palette("plasma", len(platforms)))
            ax2.set_title("Total Engagement by Platform", fontweight='bold')
            ax2.set_ylabel("Total Engagement")
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars2, total_engagements):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(total_engagements)*0.01,
                        f'{value:,}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_base64
            
        except Exception as e:
            self.logger.error(f"Error creating platform comparison chart: {e}")
            return ""
    
    async def _create_growth_chart(
        self,
        platform_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Create growth metrics chart."""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for platform, data in platform_data.items():
                if "error" in data:
                    continue
                
                metrics = data.get("metrics", [])
                if len(metrics) < 2:
                    continue
                
                timestamps = [m.timestamp for m in metrics]
                followers = [m.followers for m in metrics]
                
                ax.plot(timestamps, followers, marker='o', label=f"{platform.title()} Followers", linewidth=2)
            
            ax.set_title("Follower Growth Over Time", fontsize=16, fontweight='bold')
            ax.set_xlabel("Date")
            ax.set_ylabel("Followers")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format y-axis to show numbers with commas
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_base64
            
        except Exception as e:
            self.logger.error(f"Error creating growth chart: {e}")
            return ""
    
    async def _create_content_performance_chart(
        self,
        platform_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Create content performance scatter plot."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = sns.color_palette("Set2", len(platform_data))
            
            for i, (platform, data) in enumerate(platform_data.items()):
                if "error" in data:
                    continue
                
                metrics = data.get("metrics", [])
                if not metrics:
                    continue
                
                reach_values = [m.reach for m in metrics if m.reach > 0]
                engagement_rates = [m.engagement_rate for m in metrics if m.reach > 0]
                impressions = [m.impressions for m in metrics if m.reach > 0]
                
                if reach_values and engagement_rates:
                    scatter = ax.scatter(
                        reach_values, 
                        engagement_rates,
                        s=[i/1000 + 50 for i in impressions],  # Size based on impressions
                        alpha=0.6,
                        color=colors[i],
                        label=platform.title()
                    )
            
            ax.set_title("Content Performance: Reach vs Engagement Rate", fontsize=16, fontweight='bold')
            ax.set_xlabel("Reach")
            ax.set_ylabel("Engagement Rate (%)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Format x-axis to show numbers with commas
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_base64
            
        except Exception as e:
            self.logger.error(f"Error creating content performance chart: {e}")
            return ""
    
    async def export_report(
        self,
        report: WeeklyReport,
        output_path: str,
        format: ReportFormat = ReportFormat.HTML
    ) -> str:
        """
        Export report to specified format.
        
        Args:
            report: WeeklyReport object
            output_path: Output file path
            format: Export format
        
        Returns:
            Path to exported file
        """
        try:
            if format == ReportFormat.HTML:
                return await self._export_html_report(report, output_path)
            elif format == ReportFormat.PDF:
                return await self._export_pdf_report(report, output_path)
            elif format == ReportFormat.JSON:
                return await self._export_json_report(report, output_path)
            elif format == ReportFormat.MARKDOWN:
                return await self._export_markdown_report(report, output_path)
            elif format == ReportFormat.EXCEL:
                return await self._export_excel_report(report, output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            raise
    
    async def _export_html_report(self, report: WeeklyReport, output_path: str) -> str:
        """Export report as HTML."""
        try:
            # Generate HTML content
            html_content = self._generate_html_content(report)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report exported to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting HTML report: {e}")
            raise
    
    def _generate_html_content(self, report: WeeklyReport) -> str:
        """Generate HTML content for the report."""
        # This would generate comprehensive HTML content
        # For brevity, returning a simplified version
        
        content = f"""
        <div class="header">
            <h1>Weekly Social Media Report</h1>
            <p>Period: {report.week_start.strftime('%B %d, %Y')} - {report.week_end.strftime('%B %d, %Y')}</p>
            <p>Generated: {report.generated_at.strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="metric-card">
                <div class="metric-value">{report.summary.get('totals', {}).get('posts', 0)}</div>
                <div class="metric-label">Total Posts</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{report.summary.get('totals', {}).get('engagement', 0):,}</div>
                <div class="metric-label">Total Engagement</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{report.summary.get('averages', {}).get('engagement_rate', 0):.1f}%</div>
                <div class="metric-label">Avg Engagement Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{report.summary.get('performance', {}).get('success_rate', 0):.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Platform Performance</h2>
            {self._generate_platform_performance_html(report.platform_performance)}
        </div>
        
        <div class="section">
            <h2>Charts and Analytics</h2>
            {self._generate_charts_html(report.charts)}
        </div>
        
        <div class="section recommendations">
            <h2>Recommendations</h2>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
            </ul>
        </div>
        """
        
        return self.templates["weekly_summary"].format(content=content)
    
    def _generate_platform_performance_html(self, platform_performance: Dict[str, Dict[str, Any]]) -> str:
        """Generate HTML for platform performance section."""
        html_parts = []
        
        for platform, performance in platform_performance.items():
            if "error" in performance:
                continue
            
            metrics = performance.get("metrics", {})
            rating = performance.get("rating", "unknown")
            highlights = performance.get("highlights", [])
            concerns = performance.get("concerns", [])
            
            html_parts.append(f"""
            <div class="platform-section">
                <h3>{platform.title()}</h3>
                <p><strong>Performance Rating:</strong> {rating.replace('_', ' ').title()}</p>
                <p><strong>Engagement Rate:</strong> {metrics.get('avg_engagement_rate', 0):.1f}%</p>
                <p><strong>Total Posts:</strong> {metrics.get('posts_count', 0)}</p>
                <p><strong>Success Rate:</strong> {metrics.get('success_rate', 0):.1f}%</p>
                
                {f'<p><strong>Highlights:</strong></p><ul>{"".join(f"<li>{h}</li>" for h in highlights)}</ul>' if highlights else ''}
                {f'<p><strong>Concerns:</strong></p><ul>{"".join(f"<li>{c}</li>" for c in concerns)}</ul>' if concerns else ''}
            </div>
            """)
        
        return ''.join(html_parts)
    
    def _generate_charts_html(self, charts: Dict[str, str]) -> str:
        """Generate HTML for charts section."""
        html_parts = []
        
        chart_titles = {
            "engagement_trend": "Engagement Trend Over Time",
            "platform_comparison": "Platform Performance Comparison",
            "growth_metrics": "Follower Growth",
            "content_performance": "Content Performance Analysis"
        }
        
        for chart_name, chart_data in charts.items():
            if chart_data:
                title = chart_titles.get(chart_name, chart_name.replace('_', ' ').title())
                html_parts.append(f"""
                <div class="chart-container">
                    <h3>{title}</h3>
                    <img src="data:image/png;base64,{chart_data}" alt="{title}" style="max-width: 100%; height: auto;">
                </div>
                """)
        
        return ''.join(html_parts)
    
    async def _export_json_report(self, report: WeeklyReport, output_path: str) -> str:
        """Export report as JSON."""
        try:
            # Convert report to dictionary
            report_dict = asdict(report)
            
            # Convert datetime objects to ISO strings
            report_dict["week_start"] = report.week_start.isoformat()
            report_dict["week_end"] = report.week_end.isoformat()
            report_dict["generated_at"] = report.generated_at.isoformat()
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            self.logger.info(f"JSON report exported to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting JSON report: {e}")
            raise
    
    async def _export_markdown_report(self, report: WeeklyReport, output_path: str) -> str:
        """Export report as Markdown."""
        try:
            markdown_content = self._generate_markdown_content(report)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"Markdown report exported to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting Markdown report: {e}")
            raise
    
    def _generate_markdown_content(self, report: WeeklyReport) -> str:
        """Generate Markdown content for the report."""
        content = f"""# Weekly Social Media Report

**Period:** {report.week_start.strftime('%B %d, %Y')} - {report.week_end.strftime('%B %d, %Y')}  
**Generated:** {report.generated_at.strftime('%B %d, %Y at %I:%M %p')}

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Posts | {report.summary.get('totals', {}).get('posts', 0)} |
| Total Engagement | {report.summary.get('totals', {}).get('engagement', 0):,} |
| Average Engagement Rate | {report.summary.get('averages', {}).get('engagement_rate', 0):.1f}% |
| Success Rate | {report.summary.get('performance', {}).get('success_rate', 0):.1f}% |

## Platform Performance

"""
        
        for platform, performance in report.platform_performance.items():
            if "error" in performance:
                continue
            
            metrics = performance.get("metrics", {})
            rating = performance.get("rating", "unknown")
            
            content += f"""### {platform.title()}

- **Performance Rating:** {rating.replace('_', ' ').title()}
- **Engagement Rate:** {metrics.get('avg_engagement_rate', 0):.1f}%
- **Total Posts:** {metrics.get('posts_count', 0)}
- **Success Rate:** {metrics.get('success_rate', 0):.1f}%

"""
        
        content += f"""## Recommendations

"""
        for i, rec in enumerate(report.recommendations, 1):
            content += f"{i}. {rec}\n"
        
        return content
    
    async def _export_excel_report(self, report: WeeklyReport, output_path: str) -> str:
        """Export report as Excel file."""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Posts', 'Total Engagement', 'Avg Engagement Rate', 'Success Rate'],
                    'Value': [
                        report.summary.get('totals', {}).get('posts', 0),
                        report.summary.get('totals', {}).get('engagement', 0),
                        f"{report.summary.get('averages', {}).get('engagement_rate', 0):.1f}%",
                        f"{report.summary.get('performance', {}).get('success_rate', 0):.1f}%"
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Platform performance sheet
                platform_data = []
                for platform, performance in report.platform_performance.items():
                    if "error" not in performance:
                        metrics = performance.get("metrics", {})
                        platform_data.append({
                            'Platform': platform.title(),
                            'Engagement Rate': metrics.get('avg_engagement_rate', 0),
                            'Posts Count': metrics.get('posts_count', 0),
                            'Success Rate': metrics.get('success_rate', 0),
                            'Rating': performance.get('rating', 'unknown').replace('_', ' ').title()
                        })
                
                if platform_data:
                    pd.DataFrame(platform_data).to_excel(writer, sheet_name='Platform Performance', index=False)
                
                # Recommendations sheet
                rec_data = {'Recommendation': report.recommendations}
                pd.DataFrame(rec_data).to_excel(writer, sheet_name='Recommendations', index=False)
            
            self.logger.info(f"Excel report exported to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error exporting Excel report: {e}")
            raise

