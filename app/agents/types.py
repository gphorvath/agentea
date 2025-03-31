"""Agent types module.
This module defines the types used in the agent system, including
agent tasks and results.
It includes the following classes:
- AgentTask: Represents a task that an agent can perform.
- AgentResult: Represents the result of an agent task.
"""

from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel


class AgentStatus(str, Enum):
    """Agent status enumeration.
    This enumeration defines the possible statuses for an agent task.
    The possible statuses are:
    - IDLE: The task is idle and not currently running.
    - RUNNING: The task is currently running.
    - COMPLETED: The task has completed successfully.
    - FAILED: The task has failed.
    """

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTask(BaseModel):
    """Agent task model.
    This model represents a task that an agent can perform.
    It includes the following fields:
    - id: The unique identifier for the task.
    - name: The name of the task.
    - description: A description of the task.
    - parameters: A dictionary of parameters for the task.
    """

    id: str
    name: str
    description: str | None = None
    parameters: dict[Any, Any] = {}

    def __init__(self, **data):
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid.uuid4())
        super().__init__(**data)


class AgentResult(BaseModel):
    """Agent result model.
    This model represents the result of an agent task.
    It includes the following fields:
    - task_id: The unique identifier for the task.
    - status: The status of the task.
    - result: The result of the task.
    - error: An error message if the task failed.
    """

    task_id: str
    status: AgentStatus
    result: dict[Any, Any] | None = None
    error: str | None = None
