import json
from typing import Any
from langchain.agents.tools import BaseTool
from config import config
from walrus.client import WalrusClient
from tools.base.tools import RequireApprovalTool


class ListEnvironmentsTool(BaseTool):
    """Tool to list environments."""

    name = "list_environments"
    description = (
        "List environments of a project."
        "Input should be a project id or an empty string indicating current project in the context."
    )
    walrus_client: WalrusClient

    def _run(self, project_id: str) -> str:
        if project_id == "":
            project_id = config.CONFIG.context.project_id
        try:
            environments = self.walrus_client.list_environments(project_id)
        except Exception as e:
            return e
        if environments is not None and len(environments) > 0:
            return json.dumps(environments)
        return "No environments found."


class DeleteEnvironmentsTool(RequireApprovalTool):
    """Tool to delete environments."""

    name = "delete_environments"
    description = "Delete one or multiple environments. Input should be a list of environment ids."
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            ids = json.loads(text)
        except Exception as e:
            return e

        project_id = config.CONFIG.context.project_id
        try:
            self.walrus_client.delete_environments(project_id, ids)
        except Exception as e:
            return e

        return "Successfully deleted."


class GetEnvironmentDependencyGraphTool(BaseTool):
    """Tool to get environment dependency graph."""

    name = "get_environment_dependency_graph"
    description = (
        "Get dependency graph of an environment. Input should be an environment id."
        "Output is a json data wrapped in triple backticks, representing the dependency graph."
        "You can directly return the output to the user. No need to reformat. "
        "UI can use this data to render the graph."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        data = {
            "project_id": config.CONFIG.context.project_id,
            "environment_id": text,
        }
        # graph_data = self.walrus_client.get_environment_graph(project_id, text)
        return f"```service_graph\n{data}\n```"


class CloneEnvironmentTool(RequireApprovalTool):
    """Tool to clone an environment."""

    name = "clone_environment"
    description = (
        "Clone an environment to a new one. "
        'Input should be a json string with two keys: "original_environment_name" and "target_environment_name".'
    )

    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            data = json.loads(text)
        except Exception as e:
            return e

        project_id = config.CONFIG.context.project_id
        original_environment_name = data.get("original_environment_name")
        target_environment_name = data.get("target_environment_name")

        try:
            environment = self.walrus_client.get_environment(
                project_id, original_environment_name
            )
            services = self.walrus_client.list_services(
                project_id, original_environment_name
            )
            environment["name"] = target_environment_name
            environment["services"] = services

            self.walrus_client.create_environment(project_id, environment)
        except Exception as e:
            return e

        return "Successfully cloned."
