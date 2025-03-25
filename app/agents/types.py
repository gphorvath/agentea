# Agent status enum
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Agent task model
class AgentTask(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    parameters: dict[Any, Any] = {}

    def __init__(self, **data):
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid.uuid4())
        super().__init__(**data)


# Agent result model
class AgentResult(BaseModel):
    task_id: str
    status: AgentStatus
    result: dict[Any, Any] | None = None
    error: str | None = None
