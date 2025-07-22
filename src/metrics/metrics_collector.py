"""
Metrics Collector

This module handles collection and storage of metrics from all social media agents.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON

from ..config.config_manager import ConfigManager
from ..utils.logger import get_logger


Base = declarative_base()


class MetricType(Enum):
    """Types of metrics that can be collected."""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    FOLLOWERS = "followers"
    CONVERSION = "conversion"
    PERFORMANCE = "performance"


class AgentMetric(Base):
    """Database model for agent metrics."""
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=False)
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)


class PostRecord(Base):
    """Database model for post records."""
    __tablename__ = "post_records"
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=False)
    post_id = Column(String(200))
    content_type = Column(String(50), nullable=False)
    content_preview = Column(Text)
    hashtags = Column(JSON)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    scheduled_time = Column(DateTime)
    engagement_metrics = Column(JSON)


class PlatformMetric(Base):
    """Database model for platform-specific metrics."""
    __tablename__ = "platform_metrics"
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    collection_period = Column(String(20))  # hourly, daily, weekly
    metadata = Column(JSON)


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time."""
    agent_name: str
    platform: str
    timestamp: datetime
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0
    clicks: int = 0
    shares: int = 0
    comments: int = 0
    likes: int = 0
    followers: int = 0
    posts_count: int = 0
    success_rate: float = 0.0


class MetricsCollector:
    """
    Collects and stores metrics from all social media agents.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the metrics collector.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = get_logger("metrics_collector")
        
        # Initialize database connection
        db_config = config_manager.get_database_config()
        self.engine = create_engine(db_config["url"])
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        
        # Get metrics configuration
        self.metrics_config = config_manager.get_metrics_config()
        self.collection_interval = self.metrics_config.get("collection_interval", 3600)  # 1 hour
        self.retention_period = self.metrics_config.get("retention_period", 365)  # 1 year
        
        self.logger.info("Metrics collector initialized")
    
    async def store_metrics(
        self,
        agent_name: str,
        platform: str,
        metrics: Dict[str, Any]
    ):
        """
        Store metrics for an agent.
        
        Args:
            agent_name: Name of the agent
            platform: Platform name
            metrics: Dictionary of metrics to store
        """
        try:
            session = self.SessionLocal()
            
            timestamp = datetime.utcnow()
            
            # Store each metric as a separate record
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    metric_record = AgentMetric(
                        agent_name=agent_name,
                        platform=platform,
                        metric_type=metric_name,
                        metric_value=float(metric_value),
                        timestamp=timestamp,
                        metadata={"source": "agent_report"}
                    )
                    session.add(metric_record)
            
            session.commit()
            session.close()
            
            self.logger.debug(f"Stored metrics for {agent_name} on {platform}")
            
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
            if session:
                session.rollback()
                session.close()
    
    async def store_post_record(self, post_data: Dict[str, Any]):
        """
        Store a record of a posted content.
        
        Args:
            post_data: Dictionary containing post information
        """
        try:
            session = self.SessionLocal()
            
            post_record = PostRecord(
                agent_name=post_data.get("agent_name"),
                platform=post_data.get("platform"),
                post_id=post_data.get("post_id"),
                content_type=post_data.get("content_type"),
                content_preview=post_data.get("content_preview"),
                hashtags=post_data.get("hashtags", []),
                success=post_data.get("success", False),
                error_message=post_data.get("error_message"),
                timestamp=post_data.get("timestamp", datetime.utcnow()),
                scheduled_time=post_data.get("scheduled_time"),
                engagement_metrics={}
            )
            
            session.add(post_record)
            session.commit()
            session.close()
            
            self.logger.debug(f"Stored post record for {post_data.get('agent_name')}")
            
        except Exception as e:
            self.logger.error(f"Error storing post record: {e}")
            if session:
                session.rollback()
                session.close()
    
    async def store_platform_metrics(
        self,
        platform: str,
        metrics: Dict[str, Any],
        collection_period: str = "hourly"
    ):
        """
        Store platform-wide metrics.
        
        Args:
            platform: Platform name
            metrics: Dictionary of platform metrics
            collection_period: Period of collection (hourly, daily, weekly)
        """
        try:
            session = self.SessionLocal()
            
            timestamp = datetime.utcnow()
            
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    platform_metric = PlatformMetric(
                        platform=platform,
                        metric_name=metric_name,
                        metric_value=float(metric_value),
                        timestamp=timestamp,
                        collection_period=collection_period,
                        metadata={"auto_collected": True}
                    )
                    session.add(platform_metric)
            
            session.commit()
            session.close()
            
            self.logger.debug(f"Stored platform metrics for {platform}")
            
        except Exception as e:
            self.logger.error(f"Error storing platform metrics: {e}")
            if session:
                session.rollback()
                session.close()
    
    async def get_agent_metrics(
        self,
        agent_name: str,
        platform: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricSnapshot]:
        """
        Get metrics for a specific agent.
        
        Args:
            agent_name: Name of the agent
            platform: Platform name
            start_time: Start time for metrics (default: 24 hours ago)
            end_time: End time for metrics (default: now)
            
        Returns:
            List of metric snapshots
        """
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(days=1)
            if end_time is None:
                end_time = datetime.utcnow()
            
            session = self.SessionLocal()
            
            # Query metrics
            metrics_query = session.query(AgentMetric).filter(
                AgentMetric.agent_name == agent_name,
                AgentMetric.platform == platform,
                AgentMetric.timestamp >= start_time,
                AgentMetric.timestamp <= end_time
            ).all()
            
            # Group metrics by timestamp (rounded to hour)
            metrics_by_hour = {}
            for metric in metrics_query:
                hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                if hour_key not in metrics_by_hour:
                    metrics_by_hour[hour_key] = {}
                metrics_by_hour[hour_key][metric.metric_type] = metric.metric_value
            
            # Create snapshots
            snapshots = []
            for timestamp, metrics_data in metrics_by_hour.items():
                snapshot = MetricSnapshot(
                    agent_name=agent_name,
                    platform=platform,
                    timestamp=timestamp,
                    engagement_rate=metrics_data.get("engagement_rate", 0.0),
                    reach=int(metrics_data.get("reach", 0)),
                    impressions=int(metrics_data.get("impressions", 0)),
                    clicks=int(metrics_data.get("clicks", 0)),
                    shares=int(metrics_data.get("shares", 0)),
                    comments=int(metrics_data.get("comments", 0)),
                    likes=int(metrics_data.get("likes", 0)),
                    followers=int(metrics_data.get("followers", 0)),
                    posts_count=int(metrics_data.get("posts_created", 0)),
                    success_rate=metrics_data.get("success_rate", 0.0)
                )
                snapshots.append(snapshot)
            
            session.close()
            return sorted(snapshots, key=lambda x: x.timestamp)
            
        except Exception as e:
            self.logger.error(f"Error getting agent metrics: {e}")
            if session:
                session.close()
            return []
    
    async def get_platform_summary(
        self,
        platform: str,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get summary metrics for a platform.
        
        Args:
            platform: Platform name
            period: Summary period (daily, weekly, monthly)
            
        Returns:
            Dictionary of summary metrics
        """
        try:
            session = self.SessionLocal()
            
            # Calculate time range based on period
            end_time = datetime.utcnow()
            if period == "daily":
                start_time = end_time - timedelta(days=1)
            elif period == "weekly":
                start_time = end_time - timedelta(weeks=1)
            elif period == "monthly":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
            
            # Get post records
            posts_query = session.query(PostRecord).filter(
                PostRecord.platform == platform,
                PostRecord.timestamp >= start_time,
                PostRecord.timestamp <= end_time
            ).all()
            
            # Calculate summary metrics
            total_posts = len(posts_query)
            successful_posts = len([p for p in posts_query if p.success])
            failed_posts = total_posts - successful_posts
            success_rate = (successful_posts / total_posts * 100) if total_posts > 0 else 0
            
            # Get latest platform metrics
            latest_metrics = session.query(PlatformMetric).filter(
                PlatformMetric.platform == platform,
                PlatformMetric.timestamp >= start_time
            ).all()
            
            # Aggregate metrics
            metrics_sum = {}
            for metric in latest_metrics:
                if metric.metric_name not in metrics_sum:
                    metrics_sum[metric.metric_name] = []
                metrics_sum[metric.metric_name].append(metric.metric_value)
            
            # Calculate averages
            avg_metrics = {}
            for metric_name, values in metrics_sum.items():
                avg_metrics[f"avg_{metric_name}"] = sum(values) / len(values) if values else 0
                avg_metrics[f"total_{metric_name}"] = sum(values) if values else 0
            
            summary = {
                "platform": platform,
                "period": period,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_posts": total_posts,
                "successful_posts": successful_posts,
                "failed_posts": failed_posts,
                "success_rate": success_rate,
                **avg_metrics
            }
            
            session.close()
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting platform summary: {e}")
            if session:
                session.close()
            return {}
    
    async def get_cross_platform_summary(
        self,
        period: str = "weekly"
    ) -> Dict[str, Any]:
        """
        Get summary metrics across all platforms.
        
        Args:
            period: Summary period (daily, weekly, monthly)
            
        Returns:
            Dictionary of cross-platform metrics
        """
        try:
            platforms = ["facebook", "twitter", "instagram", "linkedin", "tiktok"]
            platform_summaries = {}
            
            for platform in platforms:
                summary = await self.get_platform_summary(platform, period)
                if summary:
                    platform_summaries[platform] = summary
            
            # Calculate totals
            total_posts = sum(s.get("total_posts", 0) for s in platform_summaries.values())
            total_successful = sum(s.get("successful_posts", 0) for s in platform_summaries.values())
            total_failed = sum(s.get("failed_posts", 0) for s in platform_summaries.values())
            overall_success_rate = (total_successful / total_posts * 100) if total_posts > 0 else 0
            
            cross_platform_summary = {
                "period": period,
                "total_posts": total_posts,
                "successful_posts": total_successful,
                "failed_posts": total_failed,
                "overall_success_rate": overall_success_rate,
                "platform_summaries": platform_summaries,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return cross_platform_summary
            
        except Exception as e:
            self.logger.error(f"Error getting cross-platform summary: {e}")
            return {}
    
    async def cleanup_old_metrics(self):
        """Clean up old metrics based on retention period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_period)
            
            session = self.SessionLocal()
            
            # Delete old agent metrics
            deleted_agent_metrics = session.query(AgentMetric).filter(
                AgentMetric.timestamp < cutoff_date
            ).delete()
            
            # Delete old post records
            deleted_post_records = session.query(PostRecord).filter(
                PostRecord.timestamp < cutoff_date
            ).delete()
            
            # Delete old platform metrics
            deleted_platform_metrics = session.query(PlatformMetric).filter(
                PlatformMetric.timestamp < cutoff_date
            ).delete()
            
            session.commit()
            session.close()
            
            self.logger.info(
                f"Cleaned up old metrics: {deleted_agent_metrics} agent metrics, "
                f"{deleted_post_records} post records, {deleted_platform_metrics} platform metrics"
            )
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")
            if session:
                session.rollback()
                session.close()
    
    async def export_metrics_to_csv(
        self,
        output_path: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """
        Export metrics to CSV file.
        
        Args:
            output_path: Path to save the CSV file
            start_time: Start time for export (default: 30 days ago)
            end_time: End time for export (default: now)
        """
        try:
            if start_time is None:
                start_time = datetime.utcnow() - timedelta(days=30)
            if end_time is None:
                end_time = datetime.utcnow()
            
            session = self.SessionLocal()
            
            # Query all metrics in the time range
            metrics_query = session.query(AgentMetric).filter(
                AgentMetric.timestamp >= start_time,
                AgentMetric.timestamp <= end_time
            ).all()
            
            # Convert to DataFrame
            metrics_data = []
            for metric in metrics_query:
                metrics_data.append({
                    "agent_name": metric.agent_name,
                    "platform": metric.platform,
                    "metric_type": metric.metric_type,
                    "metric_value": metric.metric_value,
                    "timestamp": metric.timestamp
                })
            
            df = pd.DataFrame(metrics_data)
            df.to_csv(output_path, index=False)
            
            session.close()
            
            self.logger.info(f"Exported {len(metrics_data)} metrics to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            if session:
                session.close()
    
    async def start_collection_loop(self):
        """Start the metrics collection loop."""
        self.logger.info("Starting metrics collection loop")
        
        while True:
            try:
                # Perform periodic cleanup
                await self.cleanup_old_metrics()
                
                # Sleep until next collection interval
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

