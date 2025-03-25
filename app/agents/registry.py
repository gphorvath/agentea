from .base import Agent


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent):
        self._agents[agent.name] = agent

    def get(self, name):
        if name not in self._agents:
            raise ValueError(f"Agent {name} not found")
        return self._agents.get(name)

    def list(self):
        return self._agents.keys() or []

    def deregister(self, name):
        return self._agents.pop(name, None)
