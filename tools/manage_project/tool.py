import json
from langchain.agents.tools import BaseTool
from config import config
from walrus.client import WalrusClient


class ListProjectsTool(BaseTool):
    """Tool to list projects."""

    name = "list_projects"
    description = "List projects."
    walrus_client: WalrusClient

    def _run(self, query: str) -> str:
        projects = self.walrus_client.list_projects()
        return json.dumps(projects)
