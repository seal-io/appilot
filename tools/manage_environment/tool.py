import json
from typing import Any
from langchain.agents.tools import BaseTool
from config import config
from seal.client import SealClient
from tools.base.tools import RequireApprovalTool


class ListEnvironmentsTool(BaseTool):
    """Tool to list environments."""

    name = "list_environments"
    description = "List environments of a project. Input should be a project id."
    seal_client: SealClient

    def _run(self, text: str) -> str:
        environments = self.seal_client.list_environments(text)
        return json.dumps(environments)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class DeleteEnvironmentsTool(RequireApprovalTool):
    """Tool to delete environments."""

    name = "delete_environments"
    description = (
        "Delete one or multiple environments. Input should be ids of environments."
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        project_id = config.CONFIG.context.project_id
        return self.seal_client.delete_environments(project_id, text)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class GetEnvironmentDependencyGraphTool(BaseTool):
    """Tool to get environment dependency graph."""

    name = "get_environment_dependency_graph"
    description = (
        "Get dependency graph of an environment. Input should be an environment id."
        "Output is a json data wrapped in triple backticks, representing the dependency graph."
        "You can directly return the output to the user. No need to reformat. "
        "UI can use this data to render the graph."
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        data = {
            "project_id": config.CONFIG.context.project_id,
            "environment_id": text,
        }
        # graph_data = self.seal_client.get_environment_graph(project_id, text)
        return f"```service_graph\n{data}\n```"

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")
