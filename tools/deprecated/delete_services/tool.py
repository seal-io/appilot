from langchain.agents.tools import BaseTool
from config import config
from seal.client import SealClient


class DeleteServicesTool(BaseTool):
    """Tool to delete one or multipleservices."""

    name = "delete_services"
    description = "Delete one or multiple services. Input should be ids of services."
    seal_client: SealClient

    def _run(self, query: str) -> str:
        project_id = config.Config.context.project_id
        return self.seal_client.delete_services(project_id, query)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")
