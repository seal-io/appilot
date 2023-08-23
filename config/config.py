from utils import utils
import urllib3

from walrus.client import WalrusClient

from pydantic import BaseModel
from dotenv import load_dotenv


class Context(BaseModel):
    project_id: str = ""
    project_name: str = ""
    environment_id: str = ""
    environment_name: str = ""


class Config(BaseModel):
    openai_api_key: str
    openai_api_base: str
    walrus_api_key: str
    walrus_url: str
    natural_language: str
    show_reasoning: bool
    verbose: bool
    skip_tls_verify: bool
    context: Context


CONFIG: Config


def init():
    load_dotenv()
    openai_api_base = utils.get_env("OPENAI_API_BASE")
    openai_api_key = utils.get_env("OPENAI_API_KEY")
    walrus_api_key = utils.get_env("WALRUS_API_KEY")
    walrus_url = utils.get_env("WALRUS_URL")
    natural_language = utils.get_env("NATURAL_LANGUAGE", "English")
    show_reasoning = utils.get_env_bool("SHOW_REASONING", True)
    verbose = utils.get_env_bool("VERBOSE", False)
    skip_tls_verify = utils.get_env_bool("SKIP_TLS_VERIFY", False)

    if skip_tls_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if not walrus_url:
        raise Exception("WALRUS_URL is not set")
    if not walrus_api_key:
        raise Exception("WALRUS_API_KEY is not set")
    if not openai_api_key:
        raise Exception("OPENAI_API_KEY is not set")

    global CONFIG
    context = _default_context(walrus_url, walrus_api_key)
    CONFIG = Config(
        openai_api_base=openai_api_base,
        openai_api_key=openai_api_key,
        walrus_api_key=walrus_api_key,
        walrus_url=walrus_url,
        natural_language=natural_language,
        show_reasoning=show_reasoning,
        verbose=verbose,
        skip_tls_verify=skip_tls_verify,
        context=context,
    )


def set_verbose(verbose: bool):
    global CONFIG
    CONFIG.verbose = verbose


def set_show_reasoning(show_reasoning: bool):
    global CONFIG
    CONFIG.show_reasoning = show_reasoning


def update_context(context: Context):
    global CONFIG
    if context.project_id != "" and context.project_name != "":
        CONFIG.context.project_id = context.project_id
        CONFIG.context.project_name = context.project_name
    if context.environment_id != "" and context.environment_name != "":
        CONFIG.context.environment_id = context.environment_id
        CONFIG.context.environment_name = context.environment_name


def _default_context(walrus_url: str, walrus_api_key: str) -> Context:
    walrus_client = WalrusClient(
        walrus_url,
        walrus_api_key,
        verify=False,
    )
    context = Context()
    projects = walrus_client.list_projects()
    if len(projects) > 0:
        project = projects[0]
        context = Context(
            project_id=project["id"],
            project_name=project["name"],
        )
    else:
        # no project found
        return context

    environments = walrus_client.list_environments(context.project_id)
    if len(environments) > 0:
        environment = environments[0]
        context.environment_id = environment["id"]
        context.environment_name = environment["name"]
    return context
