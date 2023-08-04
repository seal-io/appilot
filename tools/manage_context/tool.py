import json
from langchain.agents.tools import BaseTool
from config import config
from seal.client import SealClient


class CurrentContextTool(BaseTool):
    """Tool to get current project and environment context."""

    name = "current_context"
    description = "Get current project and environment context."

    def _run(self, query: str) -> str:
        return json.dumps(config.CONFIG.context.__dict__)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")


class ChangeContextTool(BaseTool):
    """Tool to change project and environment context."""

    name = "change_context"
    description = (
        "Change project and environment context."
        "Input should be a json string with 2 keys: "
        "project_name, environment_name."
    )
    seal_client: SealClient

    def _run(self, text: str) -> str:
        try:
            context = json.loads(text)
        except json.JSONDecodeError as e:
            raise e

        projects = self.seal_client.list_projects()
        for project in projects:
            if project["name"] == context["project_name"]:
                context["project_id"] = project["id"]
                break
        if "project_id" not in context:
            raise Exception("Project not found")

        environments = self.seal_client.list_environments(
            context["project_id"]
        )
        for environment in environments:
            if environment["name"] == context["environment_name"]:
                context["environment_id"] = environment["id"]
                break
        if "environment_id" not in context:
            raise Exception("Environment not found")

        config.update_context(context)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("async not supported")
