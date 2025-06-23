from typing import Any

from pydantic import BaseModel

from app.agents.types import AgentStatus


class TaskRequest(BaseModel):
    agent_name: str
    task_name: str
    description: str | None = None
    parameters: dict[Any, Any] = {}


class TaskResponse(BaseModel):
    task_id: str
    agent_name: str
    status: AgentStatus
