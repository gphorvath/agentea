from .types import AgentResult, AgentStatus, AgentTask


class Agent:
    def __init__(self, name: str, description: str | None = None):
        self.name = name
        self.description = description
        self.tasks: dict[str, AgentTask] = {}
        self.results: dict[str, AgentResult] = {}
        self.status: dict[str, AgentStatus] = {}

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Override this method to implement agent-specific task execution logic
        """
        raise NotImplementedError("Agents must implement execute_task method")

    async def run_task(self, task: AgentTask) -> str:
        """Run a task and return its ID"""
        self.tasks[task.id] = task
        self.status[task.id] = AgentStatus.RUNNING

        try:
            result = await self.execute_task(task)
            self.results[task.id] = result
            self.status[task.id] = AgentStatus.COMPLETED
        except Exception as e:
            self.results[task.id] = AgentResult(
                task_id=task.id, status=AgentStatus.FAILED, error=str(e)
            )
            self.status[task.id] = AgentStatus.FAILED

        return task.id

    def get_result(self, task_id: str) -> AgentResult:
        """Get the result for a specific task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        if task_id in self.results:
            return self.results[task_id]

        return AgentResult(
            task_id=task_id, status=self.status.get(task_id, AgentStatus.IDLE)
        )
