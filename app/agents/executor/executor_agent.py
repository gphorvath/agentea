"""Executor agent that uses Llama via Ollama to execute plans."""

from typing import Any, Dict

from app.agents.base import Agent
from app.agents.types import AgentResult, AgentStatus, AgentTask
from app.clients.ollama_client import OllamaClient


class ExecutorAgent(Agent):
    """Agent that executes plans using Llama via Ollama."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma3",
    ):
        """
        Initialize the executor agent.

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
        Execute a task based on the provided plan.

        Args:
            task: The task to execute

        Returns:
            The result of the task
        """
        if task.name == "execute_plan":
            return await self._execute_plan(task)
        elif task.name == "execute_step":
            return await self._execute_step(task)
        else:
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=f"Unknown task type: {task.name}",
            )

    async def _execute_plan(self, task: AgentTask) -> AgentResult:
        """
        Execute a complete plan.

        Args:
            task: The execution task containing the plan

        Returns:
            The execution result
        """
        try:
            # Extract parameters
            plan = task.parameters.get("plan", {})
            context = task.parameters.get("context", "")

            if not plan:
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error="Missing plan",
                )

            # Validate plan structure
            if not self._validate_plan(plan):
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error="Invalid plan structure",
                )

            # Execute each step in the plan
            steps = plan.get("steps", [])
            results = []

            for step in steps:
                step_result = await self._execute_step_internal(step, context)
                results.append(
                    {
                        "step_id": step.get("step_id"),
                        "title": step.get("title"),
                        "status": step_result.get("status"),
                        "output": step_result.get("output"),
                        "error": step_result.get("error"),
                    }
                )

                # If a step fails, mark the plan as failed
                if step_result.get("status") == "failed":
                    return AgentResult(
                        task_id=task.id,
                        status=AgentStatus.FAILED,
                        error=f"Step {step.get('step_id')} failed: {step_result.get('error')}",
                        result={
                            "plan_id": plan.get("plan_id"),
                            "title": plan.get("title"),
                            "steps_completed": len(results),
                            "total_steps": len(steps),
                            "step_results": results,
                        },
                    )

            # All steps completed successfully
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.COMPLETED,
                result={
                    "plan_id": plan.get("plan_id"),
                    "title": plan.get("title"),
                    "steps_completed": len(results),
                    "total_steps": len(steps),
                    "step_results": results,
                },
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=f"Execution error: {str(e)}",
            )

    async def _execute_step(self, task: AgentTask) -> AgentResult:
        """
        Execute a single step from a plan.

        Args:
            task: The execution task containing the step

        Returns:
            The execution result
        """
        try:
            # Extract parameters
            step = task.parameters.get("step", {})
            context = task.parameters.get("context", "")

            if not step:
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error="Missing step",
                )

            # Validate step structure
            if not self._validate_step(step):
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error="Invalid step structure",
                )

            # Execute the step
            step_result = await self._execute_step_internal(step, context)

            if step_result.get("status") == "failed":
                return AgentResult(
                    task_id=task.id,
                    status=AgentStatus.FAILED,
                    error=step_result.get("error"),
                    result={
                        "step_id": step.get("step_id"),
                        "title": step.get("title"),
                        "output": step_result.get("output"),
                    },
                )

            return AgentResult(
                task_id=task.id,
                status=AgentStatus.COMPLETED,
                result={
                    "step_id": step.get("step_id"),
                    "title": step.get("title"),
                    "output": step_result.get("output"),
                },
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                status=AgentStatus.FAILED,
                error=f"Step execution error: {str(e)}",
            )

    async def _execute_step_internal(
        self, step: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """
        Execute a single step using the LLM.

        Args:
            step: The step to execute
            context: Additional context for execution

        Returns:
            The execution result
        """
        try:
            # Construct the prompt
            prompt = self._construct_execution_prompt(step, context)

            # Define the expected output format
            output_format = {
                "status": "string",  # "completed" or "failed"
                "output": "string",  # The result of the step execution
                "error": "string",  # Error message if status is "failed"
                "notes": "string",  # Additional notes or observations
            }

            # Generate the execution result
            system_prompt = (
                "You are an execution assistant that carries out steps in a plan. "
                "For each step, you should determine how to accomplish it and provide a detailed output. "
                "If you cannot complete a step, explain why and provide an error message."
            )

            execution_result = await self.ollama_client.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                output_format=output_format,
                temperature=0.3,  # Lower temperature for more deterministic results
            )

            # Check if there was an error in generating the structured response
            if "error" in execution_result and "raw_response" in execution_result:
                return {
                    "status": "failed",
                    "output": "",
                    "error": f"Failed to generate structured execution result: {execution_result.get('error')}",
                    "notes": execution_result.get("raw_response", ""),
                }

            return execution_result

        except Exception as e:
            return {
                "status": "failed",
                "output": "",
                "error": f"Execution error: {str(e)}",
                "notes": "",
            }

    def _construct_execution_prompt(self, step: Dict[str, Any], context: str) -> str:
        """
        Construct a prompt for executing a step.

        Args:
            step: The step to execute
            context: Additional context for execution

        Returns:
            The constructed prompt
        """
        prompt = "Execute the following step:\n\n"
        prompt += f"Step ID: {step.get('step_id')}\n"
        prompt += f"Title: {step.get('title')}\n"
        prompt += f"Description: {step.get('description')}\n"
        prompt += f"Expected Outcome: {step.get('expected_outcome')}\n\n"

        if context:
            prompt += f"Context:\n{context}\n\n"

        prompt += (
            "Execute this step and provide a detailed output. "
            "If you cannot complete the step, explain why and provide an error message. "
            "Your response should include the status (completed or failed), "
            "the output of the execution, any error messages if applicable, "
            "and additional notes or observations."
        )

        return prompt

    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Validate the structure of a plan.

        Args:
            plan: The plan to validate

        Returns:
            True if the plan is valid, False otherwise
        """
        required_fields = ["plan_id", "title", "steps"]

        for field in required_fields:
            if field not in plan:
                return False

        if not isinstance(plan.get("steps"), list):
            return False

        for step in plan.get("steps", []):
            if not self._validate_step(step):
                return False

        return True

    def _validate_step(self, step: Dict[str, Any]) -> bool:
        """
        Validate the structure of a step.

        Args:
            step: The step to validate

        Returns:
            True if the step is valid, False otherwise
        """
        required_fields = ["step_id", "title", "description"]

        for field in required_fields:
            if field not in step:
                return False

        return True
