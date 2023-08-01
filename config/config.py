import json
import os
from attr import dataclass

from seal.client import SealClient


@dataclass
class _context:
    project_id: str = ""
    project_name: str = ""
    environment_id: str = ""
    environment_name: str = ""


@dataclass
class _config:
    openai_api_key: str
    seal_api_key: str
    seal_url: str
    context: _context


Config: _config


def initConfig():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    seal_api_key = os.getenv("SEAL_API_KEY")
    seal_url = os.getenv("SEAL_URL")

    if seal_url is None:
        raise Exception("SEAL_URL is not set")
    if seal_api_key is None:
        raise Exception("SEAL_API_KEY is not set")
    if openai_api_key is None:
        raise Exception("OPENAI_API_KEY is not set")

    context = _default_context(seal_url, seal_api_key)
    global Config
    Config = _config(openai_api_key, seal_api_key, seal_url, context)
    cfgs = json.dumps(Config.context.__dict__)
    print(cfgs)


def updateContext(context: _context):
    global Config
    Config.context = context


def _default_context(seal_url: str, seal_api_key: str) -> _context:
    seal_client = SealClient(
        seal_url,
        seal_api_key,
        verify=False,
    )
    context = _context()
    projects = seal_client.list_projects()
    if len(projects) > 0:
        project = projects[0]
        context = _context(
            project_id=project["id"],
            project_name=project["name"],
        )
    else:
        # no project found
        return context

    environments = seal_client.list_environments(context.project_id)
    if len(environments) > 0:
        environment = environments[0]
        context.environment_id = environment["id"]
        context.environment_name = environment["name"]
    return context
