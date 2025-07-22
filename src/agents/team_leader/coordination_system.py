"""
Coordination System

This module implements the coordination system for managing platform agents.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from ...config.config_manager import ConfigManager
from ...utils.logger import get_logger


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """Task status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CoordinationTask:
    """A coordination task for platform agents."""
    task_id: str
    task_type: str
    platform: str
    priority: TaskPriority
    status: TaskStatus
    data: Dict[str, Any]
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class CoordinationSystem:
    """
    Coordination system for managing platform agents.
    
    Handles task scheduling, execution coordination, and inter-agent communication.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the coordination system.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = get_logger("coordination_system")
        
        # Task management
        self.tasks: Dict[str, CoordinationTask] = {}
        self.task_queue: List[str] = []
        
        # Agent coordination
        self.agent_locks: Dict[str, asyncio.Lock] = {}
        self.agent_queues: Dict[str, asyncio.Queue] = {}
        
        # Coordination settings
        self.coordination_config = self._load_coordination_config()
        
        # Performance tracking
        self.coordination_metrics = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "coordination_errors": 0
        }
        
        self.logger.info("Coordination system initialized")
    
    def _load_coordination_config(self) -> Dict[str, Any]:
        """Load coordination configuration."""
        return self.config_manager.get_config().get("coordination", {
            "max_concurrent_tasks": 10,
            "task_timeout": 3600,  # 1 hour
            "retry_delay": 300,    # 5 minutes
            "health_check_interval": 600,  # 10 minutes
            "coordination_interval": 60    # 1 minute
        })
    
    async def create_task(
        self,
        task_type: str,
        platform: str,
        data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        scheduled_for: Optional[datetime] = None
    ) -> str:
        """
        Create a new coordination task.
        
        Args:
            task_type: Type of task to create
            platform: Target platform for the task
            data: Task data
            priority: Task priority
            scheduled_for: When to execute the task (None for immediate)
        
        Returns:
            Task ID
        """
        task_id = f"{task_type}_{platform}_{datetime.utcnow().timestamp()}"
        
        task = CoordinationTask(
            task_id=task_id,
            task_type=task_type,
            platform=platform,
            priority=priority,
            status=TaskStatus.PENDING,
            data=data,
            created_at=datetime.utcnow(),
            scheduled_for=scheduled_for
        )
        
        self.tasks[task_id] = task
        
        # Add to queue if not scheduled
        if scheduled_for is None or scheduled_for <= datetime.utcnow():
            await self._add_to_queue(task_id)
        
        self.coordination_metrics["tasks_created"] += 1
        self.logger.info(f"Created task {task_id}: {task_type} for {platform}")
        
        return task_id
    
    async def _add_to_queue(self, task_id: str):
        """Add task to execution queue based on priority."""
        task = self.tasks[task_id]
        
        # Insert based on priority
        if task.priority == TaskPriority.URGENT:
            self.task_queue.insert(0, task_id)
        elif task.priority == TaskPriority.HIGH:
            # Insert after urgent tasks
            insert_pos = 0
            for i, existing_task_id in enumerate(self.task_queue):
                existing_task = self.tasks[existing_task_id]
                if existing_task.priority != TaskPriority.URGENT:
                    insert_pos = i
                    break
            else:
                insert_pos = len(self.task_queue)
            self.task_queue.insert(insert_pos, task_id)
        else:
            # Normal and low priority go to the end
            self.task_queue.append(task_id)
    
    async def execute_task(self, task_id: str) -> bool:
        """
        Execute a coordination task.
        
        Args:
            task_id: ID of the task to execute
        
        Returns:
            True if successful, False otherwise
        """
        task = self.tasks.get(task_id)
        if not task:
            self.logger.error(f"Task {task_id} not found")
            return False
        
        if task.status != TaskStatus.PENDING:
            self.logger.warning(f"Task {task_id} is not pending (status: {task.status})")
            return False
        
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            
            # Execute based on task type
            success = await self._execute_task_by_type(task)
            
            if success:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                self.coordination_metrics["tasks_completed"] += 1
                
                # Update average execution time
                execution_time = (task.completed_at - task.started_at).total_seconds()
                self._update_average_execution_time(execution_time)
                
                self.logger.info(f"Task {task_id} completed successfully")
            else:
                await self._handle_task_failure(task)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {e}")
            task.error_message = str(e)
            await self._handle_task_failure(task)
            return False
    
    async def _execute_task_by_type(self, task: CoordinationTask) -> bool:
        """Execute task based on its type."""
        task_type = task.task_type
        
        if task_type == "content_creation":
            return await self._execute_content_creation_task(task)
        elif task_type == "content_posting":
            return await self._execute_content_posting_task(task)
        elif task_type == "metrics_collection":
            return await self._execute_metrics_collection_task(task)
        elif task_type == "engagement_monitoring":
            return await self._execute_engagement_monitoring_task(task)
        elif task_type == "health_check":
            return await self._execute_health_check_task(task)
        elif task_type == "brand_consistency_check":
            return await self._execute_brand_consistency_check_task(task)
        else:
            self.logger.error(f"Unknown task type: {task_type}")
            return False
    
    async def _execute_content_creation_task(self, task: CoordinationTask) -> bool:
        """Execute content creation task."""
        try:
            platform = task.platform
            data = task.data
            
            # This would coordinate with the platform agent to create content
            self.logger.info(f"Executing content creation for {platform}")
            
            # Simulate task execution
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in content creation task: {e}")
            return False
    
    async def _execute_content_posting_task(self, task: CoordinationTask) -> bool:
        """Execute content posting task."""
        try:
            platform = task.platform
            data = task.data
            
            # This would coordinate with the platform agent to post content
            self.logger.info(f"Executing content posting for {platform}")
            
            # Simulate task execution
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in content posting task: {e}")
            return False
    
    async def _execute_metrics_collection_task(self, task: CoordinationTask) -> bool:
        """Execute metrics collection task."""
        try:
            platform = task.platform
            
            # This would coordinate with the platform agent to collect metrics
            self.logger.info(f"Executing metrics collection for {platform}")
            
            # Simulate task execution
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in metrics collection task: {e}")
            return False
    
    async def _execute_engagement_monitoring_task(self, task: CoordinationTask) -> bool:
        """Execute engagement monitoring task."""
        try:
            platform = task.platform
            
            # This would coordinate with the platform agent to monitor engagement
            self.logger.info(f"Executing engagement monitoring for {platform}")
            
            # Simulate task execution
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in engagement monitoring task: {e}")
            return False
    
    async def _execute_health_check_task(self, task: CoordinationTask) -> bool:
        """Execute health check task."""
        try:
            platform = task.platform
            
            # This would check the health of the platform agent
            self.logger.info(f"Executing health check for {platform}")
            
            # Simulate task execution
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in health check task: {e}")
            return False
    
    async def _execute_brand_consistency_check_task(self, task: CoordinationTask) -> bool:
        """Execute brand consistency check task."""
        try:
            platform = task.platform
            
            # This would check brand consistency for the platform
            self.logger.info(f"Executing brand consistency check for {platform}")
            
            # Simulate task execution
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in brand consistency check task: {e}")
            return False
    
    async def _handle_task_failure(self, task: CoordinationTask):
        """Handle task failure and retry logic."""
        task.retry_count += 1
        
        if task.retry_count <= task.max_retries:
            # Schedule retry
            retry_delay = self.coordination_config.get("retry_delay", 300)
            task.scheduled_for = datetime.utcnow() + timedelta(seconds=retry_delay)
            task.status = TaskStatus.PENDING
            
            self.logger.warning(f"Task {task.task_id} failed, scheduling retry {task.retry_count}/{task.max_retries}")
            
            # Add back to queue after delay
            await asyncio.sleep(1)  # Brief delay before re-queuing
            await self._add_to_queue(task.task_id)
        else:
            # Max retries exceeded
            task.status = TaskStatus.FAILED
            self.coordination_metrics["tasks_failed"] += 1
            
            self.logger.error(f"Task {task.task_id} failed permanently after {task.max_retries} retries")
    
    def _update_average_execution_time(self, execution_time: float):
        """Update average execution time metric."""
        current_avg = self.coordination_metrics["average_execution_time"]
        completed_tasks = self.coordination_metrics["tasks_completed"]
        
        if completed_tasks == 1:
            self.coordination_metrics["average_execution_time"] = execution_time
        else:
            # Calculate running average
            new_avg = ((current_avg * (completed_tasks - 1)) + execution_time) / completed_tasks
            self.coordination_metrics["average_execution_time"] = new_avg
    
    async def process_task_queue(self):
        """Process tasks in the queue."""
        max_concurrent = self.coordination_config.get("max_concurrent_tasks", 10)
        
        # Get tasks ready for execution
        ready_tasks = []
        current_time = datetime.utcnow()
        
        for task_id in self.task_queue[:max_concurrent]:
            task = self.tasks[task_id]
            
            # Check if task is ready to execute
            if task.scheduled_for is None or task.scheduled_for <= current_time:
                ready_tasks.append(task_id)
        
        # Execute ready tasks concurrently
        if ready_tasks:
            tasks_to_execute = [self.execute_task(task_id) for task_id in ready_tasks]
            await asyncio.gather(*tasks_to_execute, return_exceptions=True)
            
            # Remove completed tasks from queue
            for task_id in ready_tasks:
                if task_id in self.task_queue:
                    self.task_queue.remove(task_id)
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and
                task.completed_at and task.completed_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        if tasks_to_remove:
            self.logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "platform": task.platform,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "scheduled_for": task.scheduled_for.isoformat() if task.scheduled_for else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "retry_count": task.retry_count,
            "error_message": task.error_message
        }
    
    def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get coordination system metrics."""
        return {
            **self.coordination_metrics,
            "active_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "queue_length": len(self.task_queue),
            "total_tasks": len(self.tasks)
        }
    
    async def schedule_recurring_tasks(self):
        """Schedule recurring coordination tasks."""
        platforms = ["facebook", "twitter", "instagram", "linkedin", "tiktok"]
        
        # Schedule daily metrics collection
        for platform in platforms:
            await self.create_task(
                task_type="metrics_collection",
                platform=platform,
                data={"collection_type": "daily"},
                priority=TaskPriority.NORMAL,
                scheduled_for=datetime.utcnow() + timedelta(hours=1)
            )
        
        # Schedule hourly engagement monitoring
        for platform in platforms:
            await self.create_task(
                task_type="engagement_monitoring",
                platform=platform,
                data={"monitoring_type": "hourly"},
                priority=TaskPriority.NORMAL,
                scheduled_for=datetime.utcnow() + timedelta(minutes=30)
            )
        
        self.logger.info("Scheduled recurring coordination tasks")
    
    async def emergency_stop_all_tasks(self):
        """Emergency stop all tasks."""
        for task in self.tasks.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                task.status = TaskStatus.CANCELLED
        
        self.task_queue.clear()
        self.logger.warning("Emergency stop: All tasks cancelled")
    
    async def get_platform_task_summary(self, platform: str) -> Dict[str, Any]:
        """Get task summary for a specific platform."""
        platform_tasks = [t for t in self.tasks.values() if t.platform == platform]
        
        return {
            "platform": platform,
            "total_tasks": len(platform_tasks),
            "pending": len([t for t in platform_tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in platform_tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed": len([t for t in platform_tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in platform_tasks if t.status == TaskStatus.FAILED]),
            "cancelled": len([t for t in platform_tasks if t.status == TaskStatus.CANCELLED])
        }

