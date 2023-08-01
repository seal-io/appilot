from langchain.agents.tools import BaseTool
from config import config
from seal.client import SealClient


class ListServicesTool(BaseTool):
    """Tool to list existing services."""

    name = "list_existing_services"
    description = "List existing services."
    seal_client: SealClient

    def _run(self, query: str) -> str:
        project_id = config.Config.context.project_id
        environment_id = config.Config.context.environment_id
        services = self.seal_client.list_services(project_id, environment_id)
        return services

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
