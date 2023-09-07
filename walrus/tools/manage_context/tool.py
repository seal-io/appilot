import json
from langchain.agents.tools import BaseTool
from walrus.client import WalrusClient
from walrus import context as walrus_context


class CurrentContextTool(BaseTool):
    """Tool to get current project and environment context."""

    name = "current_context"
    description = "Get current project and environment context."

    def _run(self, query: str) -> str:
        return json.dumps(walrus_context.GLOBAL_CONTEXT.__dict__)


class ChangeContextTool(BaseTool):
    """Tool to change project and environment context."""

    name = "change_context"
    description = (
        "Change project and environment context."
        "Input should be a json string with 2 keys: "
        "project_name, environment_name."
        "If users did not specify any of the two keys, leave it empty."
    )
    walrus_client: WalrusClient

    def _run(self, text: str) -> str:
        try:
            context = json.loads(text)
        except Exception as e:
            return e

        project_id = walrus_context.GLOBAL_CONTEXT.project_id
        if "project_name" in context and context["project_name"] != "":
            try:
                project = self.walrus_client.get_project(
                    context["project_name"]
                )
            except Exception as e:
                return e
            project_id = project["id"]
            context["project_id"] = project_id

        if "environment_name" in context and context["environment_name"] != "":
            try:
                environment = self.walrus_client.get_environment(
                    project_id, context["environment_name"]
                )
            except Exception as e:
                return e
            context["environment_id"] = environment["id"]

        walrus_context.update_context(context)
