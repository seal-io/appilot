from pydantic import BaseModel

from walrus.client import WalrusClient


class Context(BaseModel):
    project_id: str = ""
    project_name: str = ""
    environment_id: str = ""
    environment_name: str = ""


GLOBAL_CONTEXT: Context


def set_default(
    walrus_url: str,
    walrus_api_key: str,
    default_project: str = "",
    default_environment: str = "",
) -> Context:
    walrus_client = WalrusClient(
        walrus_url,
        walrus_api_key,
        verify=False,
    )
    if default_project != "" and default_environment != "":
        project = walrus_client.get_project(default_project)
        environment = walrus_client.get_environment(
            default_project, default_environment
        )
    else:
        # Get the first project and environment if not specified.
        projects = walrus_client.list_projects()
        if projects is None or len(projects) == 0:
            raise Exception("No available project. A project is required.")
        project = projects[0]
        environments = walrus_client.list_environments(project.get("id"))
        if environments is None or len(environments) == 0:
            raise Exception(
                "No aviailable environment. An environment is required."
            )
        environment = environments[0]

    global GLOBAL_CONTEXT
    GLOBAL_CONTEXT = Context(
        project_id=project.get("id"),
        project_name=project.get("name"),
        environment_id=environment.get("id"),
        environment_name=environment.get("name"),
    )


def update_context(context):
    global GLOBAL_CONTEXT
    if (
        context.get("project_id") is not None
        and context.get("project_name") != ""
    ):
        GLOBAL_CONTEXT.project_id = context.get("project_id")
        GLOBAL_CONTEXT.project_name = context.get("project_name")
    if (
        context.get("environment_id") is not None
        and context.get("environment_name") != ""
    ):
        GLOBAL_CONTEXT.environment_id = context.get("environment_id")
        GLOBAL_CONTEXT.environment_name = context.get("environment_name")
