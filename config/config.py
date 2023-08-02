import json
import os
from pydantic import BaseModel
from dotenv import load_dotenv

from seal.client import SealClient


class Context(BaseModel):
    project_id: str = ""
    project_name: str = ""
    environment_id: str = ""
    environment_name: str = ""


class Config(BaseModel):
    openai_api_key: str
    seal_api_key: str
    seal_url: str
    natural_language: str = "English"
    context: Context


CONFIG: Config


def initConfig():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    seal_api_key = os.getenv("SEAL_API_KEY")
    seal_url = os.getenv("SEAL_URL")
    natural_language = os.getenv("NATURAL_LANGUAGE")

    if seal_url is None:
        raise Exception("SEAL_URL is not set")
    if seal_api_key is None:
        raise Exception("SEAL_API_KEY is not set")
    if openai_api_key is None:
        raise Exception("OPENAI_API_KEY is not set")


    global CONFIG
    context = _default_context(seal_url, seal_api_key)
    CONFIG = Config(openai_api_key=openai_api_key, seal_api_key=seal_api_key, seal_url=seal_url, context=context)
    if natural_language is not None and natural_language.strip():
        CONFIG.natural_language = natural_language


def updateContext(context: Context):
    global CONFIG
    CONFIG.context = context


def _default_context(seal_url: str, seal_api_key: str) -> Context:
    seal_client = SealClient(
        seal_url,
        seal_api_key,
        verify=False,
    )
    context = Context()
    projects = seal_client.list_projects()
    if len(projects) > 0:
        project = projects[0]
        context = Context(
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
