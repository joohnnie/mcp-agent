"""
Task Management for Agent System.

This module provides task definitions, state tracking, and result management
for the agent system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskResult(BaseModel):
    """Result from task execution."""

    success: bool = Field(description="Whether the task completed successfully")
    data: Any = Field(default=None, description="Result data from the task")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(
        default=None, description="Task execution time in seconds"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Task(BaseModel):
    """
    Task definition for agent execution.

    A task represents a unit of work that can be executed by an agent.
    Tasks can be hierarchical, with subtasks delegated to subagents.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique task ID")
    name: str = Field(description="Human-readable task name")
    description: str = Field(description="Detailed task description")
    task_type: str = Field(description="Type of task (e.g., 'calculation', 'file_operation')")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Task-specific parameters"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority"
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING, description="Current task status"
    )
    result: Optional[TaskResult] = Field(default=None, description="Task result if completed")
    parent_task_id: Optional[str] = Field(
        default=None, description="Parent task ID if this is a subtask"
    )
    assigned_agent_id: Optional[str] = Field(
        default=None, description="ID of the agent assigned to this task"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Task creation timestamp"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Task start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Task completion timestamp"
    )
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_count: int = Field(default=0, description="Current retry count")
    timeout: Optional[float] = Field(
        default=None, description="Task timeout in seconds"
    )

    def mark_started(self) -> None:
        """Mark the task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def mark_completed(self, result: TaskResult) -> None:
        """Mark the task as completed with a result."""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark the task as failed with an error message."""
        self.status = TaskStatus.FAILED
        self.result = TaskResult(success=False, error=error)
        self.completed_at = datetime.now()

    def mark_cancelled(self) -> None:
        """Mark the task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()

    def can_retry(self) -> bool:
        """Check if the task can be retried."""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment the retry counter."""
        self.retry_count += 1
        self.status = TaskStatus.PENDING

    def get_execution_time(self) -> Optional[float]:
        """Get the task execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
