"""Planner agent that uses Llama via Ollama to create structured plans."""

from typing import List

from app.agents.base import Agent
from app.agents.types import AgentTask, AgentResult, AgentStatus
from app.clients.ollama_client import OllamaClient


class PlannerAgent(Agent):
    """Agent that generates structured plans using Llama via Ollama."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        ollama_url: str = "http://localhost:11434",
        model: str = "llama3",
    ):
        """
        Initialize the planner agent.

        Args:
            name: Name of the agent
            description: Description of the agent
            ollama_url: URL of the Ollama API
            model: Model to use for generation
        """
        super().__init__(name, description)
        self.ollama_client = OllamaClient(base_url=ollama_url, model=model)

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute a planning task.

        Args:
            task: The task to execute

        Returns:
            The result of the task
        """
        if task.name == "create_plan":
            return await self._create_plan(task)
        else:
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=f"Unknown task type: {task.name}",
            )

    async def _create_plan(self, task: AgentTask) -> AgentResult:
        """
        Create a structured plan based on the task description.

        Args:
            task: The planning task

        Returns:
            The planning result
        """
        try:
            # Extract parameters
            task_description = task.parameters.get("description", "")
            context = task.parameters.get("context", "")
            constraints = task.parameters.get("constraints", [])

            if not task_description:
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error="Missing task description",
                )

            # Construct the prompt
            prompt = self._construct_planning_prompt(
                task_description, context, constraints
            )

            # Define the expected output format
            output_format = {
                "plan_id": "string",
                "title": "string",
                "description": "string",
                "steps": [
                    {
                        "step_id": "string",
                        "title": "string",
                        "description": "string",
                        "expected_outcome": "string",
                    }
                ],
                "estimated_completion_time": "string",
                "dependencies": ["string"],
                "resources_needed": ["string"],
            }

            # Generate the plan
            system_prompt = (
                "You are a planning assistant that creates detailed, structured plans. "
                "Your plans should be comprehensive, logical, and actionable. "
                "Break down complex tasks into clear steps with specific outcomes."
            )

            plan = await self.ollama_client.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                output_format=output_format,
                temperature=0.7,
            )

            # Check if there was an error in generating the structured response
            if "error" in plan:
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error=f"Failed to generate structured plan: {plan.get('error')}",
                    result={"raw_response": plan.get("raw_response", "")},
                )

            return AgentResult(
                task_id=task.id,
                status=AgentStatus.COMPLETED,
                result={"plan": plan},
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=f"Planning error: {str(e)}",
            )

    def _construct_planning_prompt(
        self, task_description: str, context: str, constraints: List[str]
    ) -> str:
        """
        Construct a prompt for the planning task.

        Args:
            task_description: Description of the task to plan
            context: Additional context for the task
            constraints: List of constraints to consider

        Returns:
            The constructed prompt
        """
        prompt = (
            f"Create a detailed plan for the following task:\n\n{task_description}\n\n"
        )

        if context:
            prompt += f"Context:\n{context}\n\n"

        if constraints:
            prompt += "Constraints:\n"
            for i, constraint in enumerate(constraints, 1):
                prompt += f"{i}. {constraint}\n"
            prompt += "\n"

        prompt += (
            "Create a comprehensive plan with clear, actionable steps. "
            "Each step should have a specific outcome and be logically ordered. "
            "Include any dependencies between steps and resources needed."
        )

        return prompt
