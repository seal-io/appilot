import json
from langchain.agents.tools import BaseTool
from config import config
from seal.client import SealClient


class ListProjectsTool(BaseTool):
    """Tool to list projects."""

    name = "list_projects"
    description = "List projects."
    seal_client: SealClient

    def _run(self, query: str) -> str:
        projects = self.seal_client.list_projects()
        return json.dumps(projects)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
